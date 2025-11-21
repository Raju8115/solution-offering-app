import httpx
from fastapi import HTTPException, status
from jose import jwt, JWTError
from typing import Dict, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class IBMAuth:
    def __init__(self):
        self.client_id = settings.IBM_CLIENT_ID
        self.client_secret = settings.IBM_CLIENT_SECRET
        self.discovery_endpoint = settings.IBM_DISCOVERY_ENDPOINT
        self.oauth_server_url = settings.IBM_OAUTH_SERVER_URL
        self._jwks_cache: Optional[Dict] = None
        self._discovery_cache: Optional[Dict] = None

    async def get_discovery_document(self) -> Dict:
        """Fetch the OpenID Connect discovery document"""
        if self._discovery_cache:
            return self._discovery_cache
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.discovery_endpoint)
                response.raise_for_status()
                self._discovery_cache = response.json()
                return self._discovery_cache
        except Exception as e:
            logger.error(f"Failed to fetch discovery document: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

    async def get_jwks(self) -> Dict:
        """Fetch JSON Web Key Set for token validation"""
        if self._jwks_cache:
            return self._jwks_cache
        
        try:
            discovery = await self.get_discovery_document()
            jwks_uri = discovery.get("jwks_uri")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_uri)
                response.raise_for_status()
                self._jwks_cache = response.json()
                return self._jwks_cache
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

    async def verify_token(self, token: str) -> Dict:
        """Verify and decode the IBM AppID token"""
        try:
            # Get the discovery document to get issuer
            discovery = await self.get_discovery_document()
            issuer = discovery.get("issuer")
            
            # Decode without verification first to get the header
            unverified_header = jwt.get_unverified_header(token)
            
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Find the right key
            rsa_key = {}
            for key in jwks.get("keys", []):
                if key.get("kid") == unverified_header.get("kid"):
                    rsa_key = {
                        "kty": key.get("kty"),
                        "kid": key.get("kid"),
                        "use": key.get("use"),
                        "n": key.get("n"),
                        "e": key.get("e")
                    }
                    break
            
            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=issuer
            )
            
            return payload
            
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

    async def introspect_token(self, token: str) -> Dict:
        """Introspect token using IBM AppID introspection endpoint"""
        try:
            discovery = await self.get_discovery_document()
            introspection_endpoint = discovery.get("introspection_endpoint")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    introspection_endpoint,
                    data={
                        "token": token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                if not result.get("active"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token is not active"
                    )
                
                return result
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token introspection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )


ibm_auth = IBMAuth()