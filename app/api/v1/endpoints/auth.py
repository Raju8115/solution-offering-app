from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict, Optional
import logging
from authlib.integrations.base_client.errors import MismatchingStateError, OAuthError
from app.config import settings

# Import these if you have them
try:
    from app.bluegroups_auth import is_user_in_group
except ImportError:
    def is_user_in_group(email: str, group: str) -> bool:
        return True

try:
    from app.auth.dependencies import get_current_active_user, get_current_user
    from app.auth.permissions import get_user_roles
except ImportError:
    async def get_current_user(request: Request) -> Dict:
        user = request.session.get('user')
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user
    
    async def get_current_active_user(request: Request) -> Dict:
        return await get_current_user(request)
    
    async def get_user_roles(request: Request) -> Dict:
        user = request.session.get('user')
        return {"roles": user.get('roles', []) if user else []}

router = APIRouter()
logger = logging.getLogger(__name__)


def clear_oauth_state(session) -> None:
    """Clear ALL OAuth-related state from session"""
    keys_to_remove = []
    for key in list(session.keys()):
        # Clear state keys (authlib uses _state_ prefix)
        if key.startswith('_') or 'state' in key.lower():
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        try:
            del session[key]
            logger.debug(f"Cleared session key: {key}")
        except KeyError:
            pass


def clear_all_session(session) -> None:
    """Clear entire session for fresh start"""
    keys = list(session.keys())
    for key in keys:
        try:
            del session[key]
        except KeyError:
            pass
    logger.debug("Cleared all session data")


@router.get("/login")
async def login(request: Request):
    '''Start the OAuth/OIDC authorization code flow'''
    try:
        # CRITICAL: Clear ENTIRE session before new login attempt
        # This prevents state mismatch on subsequent logins
        clear_all_session(request.session)
        
        redirect_uri = str(request.url_for('auth_callback'))
        logger.info(f"Starting login flow with redirect_uri: {redirect_uri}")
        logger.debug(f"Session keys after clearing: {list(request.session.keys())}")

        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/callback")
async def auth_callback(request: Request):
    '''OAuth callback endpoint - Exchanges authorization code for tokens'''
    try:
        logger.info("Processing auth callback")
        logger.debug(f"Request URL: {request.url}")
        logger.debug(f"Session keys: {list(request.session.keys())}")
        
        from app.main import oauth
        
        # Check if we have the required state in session
        state_in_url = request.query_params.get('state')
        expected_state_key = f'_state_appid_{state_in_url}'
        
        if expected_state_key not in request.session:
            logger.warning(f"State key not found in session. Available keys: {list(request.session.keys())}")
            logger.warning("Redirecting to login for fresh start")
            clear_all_session(request.session)
            return RedirectResponse(url="/api/v1/login", status_code=302)
        
        # Try to exchange authorization code for tokens
        try:
            token = await oauth.appid.authorize_access_token(request)
        except MismatchingStateError as e:
            logger.warning(f"State mismatch detected: {e}")
            clear_all_session(request.session)
            return RedirectResponse(url="/api/v1/login", status_code=302)
        except OAuthError as e:
            logger.error(f"OAuth error during token exchange: {e}")
            clear_all_session(request.session)
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=oauth_error",
                status_code=302
            )
        except Exception as e:
            if "mismatching_state" in str(e).lower():
                logger.warning(f"State mismatch in exception: {e}")
                clear_all_session(request.session)
                return RedirectResponse(url="/api/v1/login", status_code=302)
            raise
        
        logger.info("Token exchange successful")
        
        # Get user info from ID token or userinfo endpoint
        user = None
        roles = []
        
        try:
            user = await oauth.appid.parse_id_token(request, token)
            logger.info("ID token parsed successfully")
        except Exception as e:
            logger.warning(f"Failed to parse ID token: {e}")
            try:
                user = await oauth.appid.userinfo(token=token)
            except Exception as ue:
                logger.error(f"Failed to get userinfo: {ue}")
                clear_all_session(request.session)
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error=userinfo_failed",
                    status_code=302
                )
        
        if not user:
            logger.error("No user info retrieved")
            clear_all_session(request.session)
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=no_user",
                status_code=302
            )
        
        # Get user roles from BlueGroups (with error handling)
        email = user.get("email")
        if email:
            try:
                if is_user_in_group(email, "Solution_Architect"):
                    roles.append("Solution_Architect")
                # if is_user_in_group(email, "Administration"):
                roles.append("Administration")
            except Exception as e:
                logger.warning(f"Failed to check BlueGroups: {e}")
        
        # Clear OAuth state keys but keep session active
        clear_oauth_state(request.session)
        
        # Store user info in session
        request.session['user'] = {
            'sub': user.get('sub'),
            'name': user.get('name') or f"{user.get('given_name', '')} {user.get('family_name', '')}".strip(),
            'email': email,
            'given_name': user.get('given_name'),
            'family_name': user.get('family_name'),
            'identities': user.get('identities'),
            'roles': roles,
        }
        
        # Store token for API calls
        request.session['token'] = {
            'access_token': token.get('access_token'),
            'token_type': token.get('token_type'),
            'expires_at': token.get('expires_at'),
        }
        
        logger.info(f"✅ User logged in: {email}")
        logger.info(f"✅ Roles: {roles}")
        logger.debug(f"Session keys after login: {list(request.session.keys())}")
        
        # Redirect to catalog page
        redirect_url = f"{settings.FRONTEND_URL}/catalog"
        logger.info(f"Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except MismatchingStateError:
        logger.warning("State mismatch caught at outer level")
        clear_all_session(request.session)
        return RedirectResponse(url="/api/v1/login", status_code=302)
    except Exception as e:
        logger.error(f"Auth callback error: {e}", exc_info=True)
        clear_all_session(request.session)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=auth_failed",
            status_code=302
        )


@router.get("/user")
async def get_user_profile(request: Request):
    """Get current logged-in user's profile"""
    user = request.session.get('user')
    if not user:
        return JSONResponse(
            status_code=401,
            content={'error': 'Not authenticated'}
        )
    
    return {
        'user': {
            'sub': user.get('sub'),
            'name': user.get('name'),
            'email': user.get('email'),
            'given_name': user.get('given_name'),
            'family_name': user.get('family_name'),
            'roles': user.get('roles', [])
        }
    }


@router.get("/me")
async def get_current_user_info(request: Request):
    """Get current user information including roles"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user": user,
        "roles": {"roles": user.get('roles', [])}
    }


@router.post("/logout")
@router.get("/logout")
async def logout(request: Request):
    """Logout user by invalidating session and clearing cookies"""
    W3_SLO_URL = getattr(settings, 'W3_SLO_URL', "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout")
    
    try:
        clear_all_session(request.session)
        
        response = JSONResponse(
            content={
                "message": "Logged out successfully",
                "logout_url": W3_SLO_URL,
            }
        )
        
        # Delete session cookie
        response.delete_cookie(
            key="session",
            path="/",
            domain=None,
            samesite="none",
            secure=True,
        )
        
        logger.info("✅ User logged out, session cleared.")
        return response
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": f"Logout failed: {str(e)}"}
        )


@router.get("/validate")
async def validate_session(request: Request):
    """Validate if user session is active"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        'valid': True,
        'user': {
            'email': user.get('email'),
            'name': user.get('name'),
            'roles': user.get('roles', [])
        }
    }


@router.get("/check")
async def check_auth(request: Request):
    """Check authentication status without requiring login"""
    user = request.session.get('user')
    
    logger.debug(f"Auth check - Session keys: {list(request.session.keys())}")
    logger.debug(f"Auth check - User present: {user is not None}")
    
    if user:
        return {
            'authenticated': True,
            'user': {
                'email': user.get('email'),
                'name': user.get('name'),
                'roles': user.get('roles', [])
            }
        }
    
    return {
        'authenticated': False,
        'user': None
    }


@router.get("/debug/session")
async def debug_session(request: Request):
    """Debug endpoint to check session state - REMOVE IN PRODUCTION"""
    return {
        "session_keys": list(request.session.keys()),
        "has_user": "user" in request.session,
        "has_token": "token" in request.session,
        "cookie_present": "session" in request.cookies,
        "cookies": dict(request.cookies),
    }
