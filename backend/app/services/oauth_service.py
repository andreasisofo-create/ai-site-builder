"""Servizio per gestire OAuth (Google, etc.)"""

import logging
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class OAuthService:
    """Gestisce la verifica dei token OAuth"""
    
    @staticmethod
    async def verify_google_token(access_token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica un token Google OAuth e restituisce le info utente
        
        Args:
            access_token: Token OAuth di Google
            
        Returns:
            Dict con email, name, picture, sub (google_id) o None se invalido
        """
        try:
            async with httpx.AsyncClient() as client:
                # Verifica il token con Google
                response = await client.get(
                    GOOGLE_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    # Prova con tokeninfo come fallback
                    token_response = await client.get(
                        GOOGLE_TOKEN_INFO_URL,
                        params={"access_token": access_token}
                    )
                    if token_response.status_code != 200:
                        return None
                    data = token_response.json()
                else:
                    data = response.json()
                
                # Verifica che il token sia per la nostra app
                if "aud" in data and settings.GOOGLE_CLIENT_ID:
                    if data["aud"] != settings.GOOGLE_CLIENT_ID:
                        return None
                
                return {
                    "oauth_id": data.get("id") or data.get("sub"),
                    "email": data.get("email"),
                    "full_name": data.get("name"),
                    "avatar_url": data.get("picture"),
                    "verified_email": data.get("verified_email", False),
                }
                
        except Exception as e:
            logger.error(f"Errore verifica Google token: {e}")
            return None
    
    @staticmethod
    async def verify_google_id_token(id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica un ID Token Google (JWT) - usato da NextAuth
        
        Args:
            id_token: ID Token JWT di Google
            
        Returns:
            Dict con email, name, picture, sub (google_id) o None se invalido
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GOOGLE_TOKEN_INFO_URL,
                    params={"id_token": id_token}
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                
                # Verifica audience
                if settings.GOOGLE_CLIENT_ID:
                    if data.get("aud") != settings.GOOGLE_CLIENT_ID:
                        return None
                
                return {
                    "oauth_id": data.get("sub"),
                    "email": data.get("email"),
                    "full_name": data.get("name"),
                    "avatar_url": data.get("picture"),
                    "verified_email": data.get("email_verified", False),
                }
                
        except Exception as e:
            logger.error(f"Errore verifica Google ID token: {e}")
            return None


    @staticmethod
    async def verify_microsoft_token(access_token: str) -> Optional[Dict[str, Any]]:
        """Verifica un token Microsoft e restituisce le info utente"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.microsoft.com/v1.0/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code != 200:
                    logger.error(f"Microsoft userinfo failed: {response.text}")
                    return None

                data = response.json()

                return {
                    "oauth_id": data.get("id"),
                    "email": data.get("mail") or data.get("userPrincipalName"),
                    "full_name": data.get("displayName"),
                    "avatar_url": None,
                    "verified_email": True,
                }

        except Exception as e:
            logger.error(f"Errore verifica Microsoft token: {e}")
            return None


oauth_service = OAuthService()
