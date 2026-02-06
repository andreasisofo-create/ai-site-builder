"""Routes per autenticazione"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User
from app.services.oauth_service import oauth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============= SCHEMAS =============

class OAuthLoginRequest(BaseModel):
    provider: str  # 'google', 'github', etc.
    access_token: Optional[str] = None
    id_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ============= ROUTES =============

@router.post("/register")
async def register(email: str, password: str, full_name: str = "", db: Session = Depends(get_db)):
    """Registra un nuovo utente"""
    # Verifica se esiste già
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email già registrata")
    
    # Crea utente
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Utente creato", "user_id": user.id}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login utente"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name}
    }


@router.post("/oauth", response_model=TokenResponse)
async def oauth_login(data: OAuthLoginRequest, db: Session = Depends(get_db)):
    """
    Login/Registrazione via OAuth (Google, etc.)
    
    - Per Google: invia id_token (JWT) o access_token
    """
    if data.provider == "google":
        # Verifica il token con Google
        if data.id_token:
            user_info = await oauth_service.verify_google_id_token(data.id_token)
        elif data.access_token:
            user_info = await oauth_service.verify_google_token(data.access_token)
        else:
            raise HTTPException(status_code=400, detail="Token mancante")
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Token OAuth non valido")
        
        if not user_info.get("verified_email"):
            raise HTTPException(status_code=400, detail="Email non verificata")
        
        # Cerca utente esistente
        user = db.query(User).filter(User.oauth_id == user_info["oauth_id"]).first()
        
        if not user:
            # Cerca per email
            user = db.query(User).filter(User.email == user_info["email"]).first()
            
            if user:
                # Collega OAuth all'account esistente
                user.oauth_provider = "google"
                user.oauth_id = user_info["oauth_id"]
                if not user.avatar_url:
                    user.avatar_url = user_info.get("avatar_url")
            else:
                # Crea nuovo utente
                user = User(
                    email=user_info["email"],
                    full_name=user_info["full_name"],
                    avatar_url=user_info.get("avatar_url"),
                    oauth_provider="google",
                    oauth_id=user_info["oauth_id"],
                    hashed_password=None,  # No password per OAuth
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
        
        # Genera JWT
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Provider '{data.provider}' non supportato")


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Ottiene info utente corrente con informazioni generazioni"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token non valido")
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "oauth_provider": user.oauth_provider,
        "is_premium": user.is_premium,
        "generations_used": user.generations_used,
        "generations_limit": user.generations_limit,
        "remaining_generations": user.remaining_generations,
        "has_remaining_generations": user.has_remaining_generations,
    }


@router.get("/quota")
async def get_quota(current_user: User = Depends(get_current_active_user)):
    """Ottiene solo le informazioni sulle quote/generazioni"""
    return {
        "is_premium": current_user.is_premium,
        "generations_used": current_user.generations_used,
        "generations_limit": current_user.generations_limit,
        "remaining_generations": current_user.remaining_generations,
        "has_remaining_generations": current_user.has_remaining_generations,
    }
