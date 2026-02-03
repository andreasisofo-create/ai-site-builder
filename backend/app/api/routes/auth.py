"""Routes per autenticazione"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


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


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Ottiene info utente corrente"""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token non valido")
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    
    return {"id": user.id, "email": user.email, "full_name": user.full_name}
