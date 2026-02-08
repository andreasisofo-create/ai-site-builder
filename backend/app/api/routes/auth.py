"""Routes per autenticazione"""

import secrets
import base64
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token, get_current_active_user
from app.models.user import User
from app.services.oauth_service import oauth_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============= SCHEMAS =============

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class OAuthLoginRequest(BaseModel):
    provider: str  # 'google', 'github', etc.
    access_token: Optional[str] = None
    id_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ============= GOOGLE OAUTH CONFIG =============

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


# ============= ROUTES =============

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuovo utente"""
    # Verifica se esiste già
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email già registrata")

    # Crea utente
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Utente creato", "user_id": user.id}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login utente"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    if user.email.lower() == "andrea.sisofo@e-quipe.it" and not user.is_premium:
        user.is_premium = True
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_premium": user.is_premium,
        }
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
        
        # Admin/Premium override
        if user.email.lower() == "andrea.sisofo@e-quipe.it" and not user.is_premium:
            user.is_premium = True
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


@router.get("/oauth/google")
async def google_oauth_redirect(redirect_to: Optional[str] = None):
    """
    Reindirizza l'utente a Google per l'autenticazione OAuth
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth non configurato")
    
    # Genera state per sicurezza
    state = secrets.token_urlsafe(32)
    
    # Determina la callback URL corretta
    if settings.RENDER_EXTERNAL_URL:
        callback_url = f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/callback"
    else:
        callback_url = "http://localhost:8000/api/auth/oauth/callback"

    # Costruisci URL di autorizzazione Google
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": callback_url,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    # Aggiungi state che include anche il redirect_to (codificato)
    state_data = f"{state}:{base64.urlsafe_b64encode(redirect_to.encode()).decode() if redirect_to else ''}"
    params["state"] = state_data
    
    auth_url = f"{GOOGLE_AUTH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    return RedirectResponse(url=auth_url)


@router.get("/oauth/callback")
async def google_oauth_callback(
    request: Request,
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Callback da Google OAuth - scambia il codice con un token e autentica l'utente
    """
    # Gestisci errori
    if error:
        return RedirectResponse(url=f"/auth?error={error}")
    
    if not code:
        return RedirectResponse(url="/auth?error=no_code")
    
    # Verifica state (CSRF protection) - opzionale per semplicità
    # stored_state = request.cookies.get("oauth_state")
    # if not state or state != stored_state:
    #     return RedirectResponse(url="/auth?error=invalid_state")
    
    try:
        # Determina la callback URL corretta (deve matchare quella usata nel redirect)
        if settings.RENDER_EXTERNAL_URL:
            redirect_uri = f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/callback"
        else:
            redirect_uri = "http://localhost:8000/api/auth/oauth/callback"
        
        # Scambia il codice con un token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            
            if token_response.status_code != 200:
                print(f"Token exchange failed: {token_response.text}")
                return RedirectResponse(url="/auth?error=token_exchange_failed")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")
        
        # Ottieni info utente
        if id_token:
            user_info = await oauth_service.verify_google_id_token(id_token)
        elif access_token:
            user_info = await oauth_service.verify_google_token(access_token)
        else:
            return RedirectResponse(url="/auth?error=no_token")
        
        if not user_info:
            return RedirectResponse(url="/auth?error=invalid_token")
        
        # Cerca o crea utente
        user = db.query(User).filter(User.oauth_id == user_info["oauth_id"]).first()
        
        if not user:
            user = db.query(User).filter(User.email == user_info["email"]).first()
            
            if user:
                user.oauth_provider = "google"
                user.oauth_id = user_info["oauth_id"]
                if not user.avatar_url:
                    user.avatar_url = user_info.get("avatar_url")
            else:
                user = User(
                    email=user_info["email"],
                    full_name=user_info["full_name"],
                    avatar_url=user_info.get("avatar_url"),
                    oauth_provider="google",
                    oauth_id=user_info["oauth_id"],
                    hashed_password=None,
                )
                db.add(user)
            
            db.commit()
            db.refresh(user)
        
        # Admin override
        if user.email.lower() == "andrea.sisofo@e-quipe.it" and not user.is_premium:
            user.is_premium = True
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Genera JWT
        jwt_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        # Reindirizza al frontend con il token
        # Estrai redirect_to dallo state (formato: state:base64_redirect)
        frontend_redirect = "http://localhost:3000/auth/callback"  # default
        if state and ":" in state:
            try:
                _, encoded_redirect = state.split(":", 1)
                if encoded_redirect:
                    frontend_redirect = base64.urlsafe_b64decode(encoded_redirect.encode()).decode()
            except:
                pass
             
        return RedirectResponse(url=f"{frontend_redirect}?token={jwt_token}")
        
    except Exception as e:
        print(f"Errore OAuth callback: {e}")
        return RedirectResponse(url="/auth?error=server_error")


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


@router.post("/migrate-db")
async def migrate_db(db: Session = Depends(get_db)):
    """
    Endpoint admin per migrare il database.
    Aggiunge colonne mancanti alla tabella users.
    """
    from sqlalchemy import text, inspect
    from app.core.database import engine
    
    try:
        # Lista colonne da aggiungere con i loro tipi SQL
        columns_to_add = [
            ("oauth_id", "VARCHAR"),
            ("oauth_provider", "VARCHAR"),
            ("avatar_url", "VARCHAR"),
            ("generations_used", "INTEGER DEFAULT 0"),
            ("generations_limit", "INTEGER DEFAULT 2"),
            ("is_premium", "BOOLEAN DEFAULT FALSE"),
        ]
        
        # Ottieni colonne esistenti
        inspector = inspect(engine)
        existing_columns = {col['name'] for col in inspector.get_columns('users')}
        
        added = []
        skipped = []
        errors = []
        
        for col_name, col_type in columns_to_add:
            if col_name in existing_columns:
                skipped.append(col_name)
                continue
            
            try:
                # SQLite supporta ADD COLUMN
                db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                db.commit()
                added.append(col_name)
            except Exception as e:
                db.rollback()
                # Se fallisce (es: duplicato non rilevato), logga e continua
                errors.append(f"{col_name}: {str(e)}")
        
        return {
            "success": True,
            "added_columns": added,
            "skipped_columns": skipped,
            "errors": errors,
            "message": f"Migrazione completata. Aggiunte: {len(added)}, Saltate: {len(skipped)}, Errori: {len(errors)}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Errore durante la migrazione"
        }
