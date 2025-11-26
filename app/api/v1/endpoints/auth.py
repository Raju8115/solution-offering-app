from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict
import logging
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


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
    """Start the OAuth/OIDC authorization code flow"""
    try:
        # Clear session before new login
        clear_all_session(request.session)
        
        redirect_uri = str(request.url_for('auth_callback'))
        logger.info(f"Starting login flow with redirect_uri: {redirect_uri}")

        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """OAuth callback endpoint - Exchanges authorization code for tokens"""
    try:
        logger.info("Processing auth callback")
        logger.debug(f"Request URL: {request.url}")
        logger.debug(f"Session keys: {list(request.session.keys())}")
        logger.debug(f"Cookies: {dict(request.cookies)}")
        
        from app.main import oauth
        
        # Don't do manual state checking - let authlib handle it
        # If state mismatch, we'll catch the exception and retry
        
        try:
            token = await oauth.appid.authorize_access_token(request)
        except Exception as e:
            error_msg = str(e).lower()
            if "mismatching_state" in error_msg or "state" in error_msg:
                logger.warning(f"State mismatch detected: {e}")
                # Clear session and redirect to frontend login page (not /api/v1/login to avoid loop)
                clear_all_session(request.session)
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error=session_expired",
                    status_code=302
                )
            logger.error(f"Token exchange error: {e}", exc_info=True)
            clear_all_session(request.session)
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=auth_failed",
                status_code=302
            )
        
        logger.info("Token exchange successful")
        
        # Get user info
        user = None
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
        
        email = user.get("email")
        
        # ============================================================
        # GIVE ALL USERS ADMIN ACCESS - All roles enabled
        # ============================================================
        roles = ["admin", "Solution_Architect", "Administration", "user"]
        
        # Clear OAuth state keys
        keys_to_remove = [k for k in list(request.session.keys()) if k.startswith('_')]
        for key in keys_to_remove:
            try:
                del request.session[key]
            except KeyError:
                pass
        
        # Store user info in session
        request.session['user'] = {
            'sub': user.get('sub'),
            'name': user.get('name') or f"{user.get('given_name', '')} {user.get('family_name', '')}".strip(),
            'email': email,
            'given_name': user.get('given_name'),
            'family_name': user.get('family_name'),
            'identities': user.get('identities'),
            'roles': roles,  # All users get all roles
            'is_admin': True,  # All users are admin
        }
        
        # Store token for API calls
        request.session['token'] = {
            'access_token': token.get('access_token'),
            'token_type': token.get('token_type'),
            'expires_at': token.get('expires_at'),
        }
        
        logger.info(f"✅ User logged in: {email}")
        logger.info(f"✅ Roles: {roles}")
        
        # Redirect to catalog page
        redirect_url = f"{settings.FRONTEND_URL}/catalog"
        logger.info(f"Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
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
            'roles': user.get('roles', []),
            'is_admin': user.get('is_admin', True),  # Default to True
        }
    }


@router.get("/me")
async def get_current_user_info(request: Request):
    """Get current user information including roles"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Ensure user always has admin roles
    roles = user.get('roles', ["admin", "Solution_Architect", "Administration", "user"])
    
    return {
        "user": {**user, "is_admin": True},
        "roles": {"roles": roles}
    }


@router.post("/logout")
@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    W3_SLO_URL = getattr(settings, 'W3_SLO_URL', "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout")
    
    try:
        clear_all_session(request.session)
        
        response = JSONResponse(
            content={
                "message": "Logged out successfully",
                "logout_url": W3_SLO_URL,
            }
        )
        
        response.delete_cookie(
            key="session",
            path="/",
            samesite="lax",
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
            'roles': user.get('roles', ["admin"]),
            'is_admin': True
        }
    }


@router.get("/check")
async def check_auth(request: Request):
    """Check authentication status without requiring login"""
    user = request.session.get('user')
    
    if user:
        return {
            'authenticated': True,
            'user': {
                'email': user.get('email'),
                'name': user.get('name'),
                'roles': user.get('roles', ["admin", "Solution_Architect", "Administration", "user"]),
                'is_admin': True
            }
        }
    
    return {
        'authenticated': False,
        'user': None
    }


@router.get("/debug/session")
async def debug_session(request: Request):
    """Debug endpoint to check session state"""
    return {
        "session_keys": list(request.session.keys()),
        "has_user": "user" in request.session,
        "has_token": "token" in request.session,
        "cookie_present": "session" in request.cookies,
        "cookies": dict(request.cookies),
        "user": request.session.get('user'),
    }
