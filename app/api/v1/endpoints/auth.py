from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict
import logging
from app.bluegroups_auth import is_user_in_group
from app.config import settings
from app.auth.dependencies import get_current_active_user, get_current_user
from app.auth.permissions import get_user_roles
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login")
async def login(request: Request):
    """
    Start the OAuth/OIDC authorization code flow
    Redirects user to IBM AppID login page
    """
    try:
        redirect_uri = str(request.url_for('auth_callback'))
        logger.info(f"Starting login flow with redirect_uri: {redirect_uri}")
        
        # Use the oauth instance from main.py
        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        logger.info("Processing auth callback")
        
        from app.main import oauth
        
        # Exchange authorization code for tokens
        token = await oauth.appid.authorize_access_token(request)
        logger.info("Token exchange successful")
        
        # Get user info
        try:
            user = await oauth.appid.parse_id_token(request, token)
            email = user.get("email")
            roles = []
            if is_user_in_group(email, "Solution_Architect"):
                roles.append("Solution_Architect")
            if is_user_in_group(email, "Administration"):
                roles.append("Administration")
        except Exception as e:
            logger.warning(f"Failed to parse ID token: {e}")
            user = await oauth.appid.userinfo(token=token)
        
        # Store user info in session
        request.session['user'] = {
            'sub': user.get('sub'),
            'name': user.get('name') or f"{user.get('given_name', '')} {user.get('family_name', '')}".strip(),
            'email': user.get('email'),
            'given_name': user.get('given_name'),
            'family_name': user.get('family_name'),
            'identities': user.get('identities'),
        }
        
        request.session['token'] = {
            'access_token': token.get('access_token'),
            'token_type': token.get('token_type'),
            'expires_at': token.get('expires_at'),
        }
        
        # ✅ CRITICAL: Force session to be saved
        request.session.update(request.session)
        
        logger.info(f"✅ Session saved for user: {user.get('email')}")
        logger.info(f"Session ID: {request.session.get('_id', 'NO_ID')}")
        
        # ✅ Create response with explicit cookie setting
        response = RedirectResponse(
            url=f"{settings.FRONTEND_URL}/catalog",
            status_code=302
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Auth callback error: {e}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=auth_failed")


@router.get("/user")
async def get_user_profile(request: Request, roles: dict = Depends(get_user_roles)):
    """
    Get current logged-in user's profile
    """
    user = request.session.get('user')
    if not user:
        return JSONResponse(
            status_code=401,
            content={'error': 'Not authenticated'}
        )
    roles: dict = Depends(get_user_roles)
    
    return {
        'user': {
            'sub': user.get('sub'),
            'name': user.get('name'),
            'email': user.get('email'),
            'given_name': user.get('given_name'),
            'family_name': user.get('family_name'),
            "roles": roles
        }
    }

@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    roles: dict = Depends(get_user_roles)
):
    """
    Get current user information including BlueGroup-based roles
    """
    return {
        "user": current_user,
        "roles": roles
    }

@router.post("/logout")
async def logout(request: Request):
    """
    Logout user by invalidating session, clearing cookies,
    and returning the W3 SAML logout URL.
    """

    W3_SLO_URL="https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout"
    try:
        # 1️⃣ Clear the server-side session
        request.session.clear()

        # 2️⃣ Build the logout URL for IBM W3 SAML (same as Spring)
        logout_url = W3_SLO_URL

        # 3️⃣ Expire the session cookie manually
        response = JSONResponse(
            content={
                "message": "Logged out successfully",
                "logout_url": logout_url,
            }
        )

        # Delete session cookie
        response.set_cookie(
            key="session",
            value="",
            httponly=True,
            secure=True,
            samesite="none",
            max_age=0,
            expires=0,
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
async def validate_session(current_user: Dict = Depends(get_current_user)):
    """
    Validate if user session is active
    """
    return {
        'valid': True,
        'user': {
            'email': current_user.get('email'),
            'name': current_user.get('name')
        }
    }


@router.get("/check")
async def check_auth(request: Request):
    """Check authentication status without requiring login"""
    
    session_id = request.cookies.get('session', 'NO_COOKIE')
    user = request.session.get('user')
    
    logger.info(f"=== AUTH CHECK ===")
    logger.info(f"Session Cookie: {session_id[:20]}..." if len(session_id) > 20 else session_id)
    logger.info(f"Session Data: {dict(request.session)}")
    logger.info(f"User in session: {user is not None}")
    logger.info(f"==================")
    
    if user:
        return {
            'authenticated': True,
            'user': {
                'email': user.get('email'),
                'name': user.get('name')
            }
        }
    
    return {
        'authenticated': False,
        'user': None
    }



# roles = user.get("roles", [])
# if any(r in roles for r in allowed_groups):
#     return user