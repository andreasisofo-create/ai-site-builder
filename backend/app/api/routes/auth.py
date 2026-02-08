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


# ============= OAUTH CONFIG =============

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

FRONTEND_URL = "https://site-generator-v2.vercel.app"


# ============= ROUTES =============

@router.post("/register")
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuovo utente"""
    # Verifica se esiste già
    existing = db.query(User).filter(User.email.ilike(data.email)).first()
    if existing:
        # Se l'utente esiste ma non ha password (OAuth), imposta la password
        if not existing.hashed_password:
            existing.hashed_password = get_password_hash(data.password)
            if data.full_name:
                existing.full_name = data.full_name
            db.commit()
            db.refresh(existing)
            return {"message": "Password impostata", "user_id": existing.id}
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
    user = db.query(User).filter(User.email.ilike(form_data.username)).first()
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
            user = db.query(User).filter(User.email.ilike(user_info["email"])).first()
            
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

    from urllib.parse import urlencode
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
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
    frontend_auth = f"{FRONTEND_URL}/auth"
    frontend_callback = f"{FRONTEND_URL}/auth/callback"

    # Gestisci errori
    if error:
        return RedirectResponse(url=f"{frontend_auth}?error={error}")

    if not code:
        return RedirectResponse(url=f"{frontend_auth}?error=no_code")

    try:
        # Determina la callback URL corretta (deve matchare quella usata nel redirect)
        if settings.RENDER_EXTERNAL_URL:
            redirect_uri = f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/callback"
        else:
            redirect_uri = "http://localhost:8000/api/auth/oauth/callback"

        print(f"OAuth callback - redirect_uri: {redirect_uri}")
        print(f"OAuth callback - client_id: {settings.GOOGLE_CLIENT_ID[:20]}...")
        print(f"OAuth callback - client_secret set: {bool(settings.GOOGLE_CLIENT_SECRET)}")

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
                error_detail = token_response.text
                print(f"Token exchange failed ({token_response.status_code}): {error_detail}")
                # Includi dettaglio errore nel redirect per debug
                from urllib.parse import quote
                return RedirectResponse(
                    url=f"{frontend_auth}?error=token_exchange_failed&detail={quote(error_detail[:200])}"
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")

        # Ottieni info utente
        if id_token:
            user_info = await oauth_service.verify_google_id_token(id_token)
        elif access_token:
            user_info = await oauth_service.verify_google_token(access_token)
        else:
            return RedirectResponse(url=f"{frontend_auth}?error=no_token")

        if not user_info:
            return RedirectResponse(url=f"{frontend_auth}?error=invalid_token")

        # Cerca o crea utente
        user = db.query(User).filter(User.oauth_id == user_info["oauth_id"]).first()

        if not user:
            user = db.query(User).filter(User.email.ilike(user_info["email"])).first()

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
        final_redirect = frontend_callback
        if state and ":" in state:
            try:
                _, encoded_redirect = state.split(":", 1)
                if encoded_redirect:
                    final_redirect = base64.urlsafe_b64decode(encoded_redirect.encode()).decode()
            except:
                pass

        return RedirectResponse(url=f"{final_redirect}?token={jwt_token}")

    except Exception as e:
        print(f"Errore OAuth callback: {e}")
        from urllib.parse import quote
        return RedirectResponse(url=f"{frontend_auth}?error=server_error&detail={quote(str(e)[:200])}")


@router.get("/oauth/microsoft")
async def microsoft_oauth_redirect(redirect_to: Optional[str] = None):
    """Reindirizza l'utente a Microsoft per l'autenticazione OAuth"""
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Microsoft OAuth non configurato")

    state = secrets.token_urlsafe(32)

    if settings.RENDER_EXTERNAL_URL:
        callback_url = f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/microsoft/callback"
    else:
        callback_url = "http://localhost:8000/api/auth/oauth/microsoft/callback"

    from urllib.parse import urlencode
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": callback_url,
        "response_type": "code",
        "scope": "openid email profile User.Read",
        "state": f"{state}:{base64.urlsafe_b64encode(redirect_to.encode()).decode() if redirect_to else ''}",
        "prompt": "select_account",
    }

    auth_url = f"{MICROSOFT_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/oauth/microsoft/callback")
async def microsoft_oauth_callback(
    request: Request,
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Callback da Microsoft OAuth"""
    frontend_auth = f"{FRONTEND_URL}/auth"
    frontend_callback = f"{FRONTEND_URL}/auth/callback"

    if error:
        return RedirectResponse(url=f"{frontend_auth}?error={error}")

    if not code:
        return RedirectResponse(url=f"{frontend_auth}?error=no_code")

    try:
        if settings.RENDER_EXTERNAL_URL:
            redirect_uri = f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/microsoft/callback"
        else:
            redirect_uri = "http://localhost:8000/api/auth/oauth/microsoft/callback"

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                MICROSOFT_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.MICROSOFT_CLIENT_ID,
                    "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                    "scope": "openid email profile User.Read",
                }
            )

            if token_response.status_code != 200:
                error_detail = token_response.text
                print(f"Microsoft token exchange failed: {error_detail}")
                from urllib.parse import quote
                return RedirectResponse(
                    url=f"{frontend_auth}?error=token_exchange_failed&detail={quote(error_detail[:200])}"
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")

        user_info = await oauth_service.verify_microsoft_token(access_token)

        if not user_info or not user_info.get("email"):
            return RedirectResponse(url=f"{frontend_auth}?error=invalid_token")

        # Cerca o crea utente
        user = db.query(User).filter(User.oauth_id == user_info["oauth_id"]).first()

        if not user:
            user = db.query(User).filter(User.email.ilike(user_info["email"])).first()

            if user:
                user.oauth_provider = "microsoft"
                user.oauth_id = user_info["oauth_id"]
            else:
                user = User(
                    email=user_info["email"],
                    full_name=user_info["full_name"],
                    oauth_provider="microsoft",
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

        jwt_token = create_access_token(data={"sub": str(user.id), "email": user.email})

        final_redirect = frontend_callback
        if state and ":" in state:
            try:
                _, encoded_redirect = state.split(":", 1)
                if encoded_redirect:
                    final_redirect = base64.urlsafe_b64decode(encoded_redirect.encode()).decode()
            except:
                pass

        return RedirectResponse(url=f"{final_redirect}?token={jwt_token}")

    except Exception as e:
        print(f"Errore Microsoft OAuth callback: {e}")
        from urllib.parse import quote
        return RedirectResponse(url=f"{frontend_auth}?error=server_error&detail={quote(str(e)[:200])}")


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


@router.get("/debug-oauth")
async def debug_oauth():
    """Debug: mostra configurazione OAuth (senza segreti)"""
    return {
        "google_client_id_set": bool(settings.GOOGLE_CLIENT_ID),
        "google_client_id_prefix": settings.GOOGLE_CLIENT_ID[:20] + "..." if settings.GOOGLE_CLIENT_ID else "NOT SET",
        "google_client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
        "google_client_secret_length": len(settings.GOOGLE_CLIENT_SECRET) if settings.GOOGLE_CLIENT_SECRET else 0,
        "render_external_url": settings.RENDER_EXTERNAL_URL or "NOT SET",
        "callback_url": f"{settings.RENDER_EXTERNAL_URL}/api/auth/oauth/callback" if settings.RENDER_EXTERNAL_URL else "NOT SET",
        "frontend_url": FRONTEND_URL,
    }


@router.post("/set-password")
async def set_password(data: RegisterRequest, db: Session = Depends(get_db)):
    """Imposta password per un account OAuth (senza password)"""
    user = db.query(User).filter(User.email.ilike(data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    if user.hashed_password:
        raise HTTPException(status_code=400, detail="L'utente ha gia' una password")

    try:
        user.hashed_password = get_password_hash(data.password)
    except Exception as e:
        # Fallback: usa bcrypt direttamente se passlib fallisce
        import bcrypt
        salt = bcrypt.gensalt()
        user.hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), salt).decode('utf-8')

    if data.full_name:
        user.full_name = data.full_name

    db.commit()
    db.refresh(user)

    return {"message": "Password impostata", "user_id": user.id}


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
