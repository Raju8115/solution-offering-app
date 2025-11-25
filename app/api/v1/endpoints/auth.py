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


# ==========================================================
#  LOGIN (start OAuth2 flow)
# ==========================================================
@router.get("/login")
async def login(request: Request):
    """
    Start IBM AppID login flow.
    Always clears old session to avoid STATE MISMATCH errors.
    """
    try:
        # Clear stale session to prevent CSRF/state mismatch
        request.session.clear()

        redirect_uri = str(request.url_for("auth_callback"))
        logger.info(f"[LOGIN] redirect_uri = {redirect_uri}")

        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)

    except Exception as e:
        logger.error(f"[LOGIN ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


# ==========================================================
#  CALLBACK (App ID calls this after login)
# ==========================================================
@router.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        logger.info("[CALLBACK] Processing auth callback...")

        from app.main import oauth

        # 1️⃣ Exchange authorization code for tokens
        token = await oauth.appid.authorize_access_token(request)
        logger.info("[CALLBACK] Token exchange OK")

        # 2️⃣ Get user claims
        try:
            user = await oauth.appid.parse_id_token(request, token)
        except:
            logger.warning("[CALLBACK] Failed to parse ID token, using userinfo()")
            user = await oauth.appid.userinfo(token=token)

        email = user.get("email")
        name = user.get("name") or f"{user.get('given_name', '')} {user.get('family_name', '')}".strip()

        # ==========================================================
        # 3️⃣ ASSIGN EVERY USER AS ADMIN (your requirement)
        # ==========================================================
        roles = ["admin"]

        # ==========================================================
        # 4️⃣ SAVE EXACT SESSION STRUCTURE REACT EXPECTS
        # ==========================================================
        request.session["user"] = {
            "sub": user.get("sub"),
            "name": name,
            "email": email,
            "given_name": user.get("given_name"),
            "family_name": user.get("family_name"),
            "identities": user.get("identities"),
            "roles": roles,                   # important
        }

        request.session["token"] = {
            "access_token": token.get("access_token"),
            "token_type": token.get("token_type"),
            "expires_at": token.get("expires_at"),
            "id_token": token.get("id_token"),  # important for React
        }

        request.session.update(request.session)  # Force save

        logger.info(f"[CALLBACK] Session saved for {email}")

        # 5️⃣ Redirect to frontend
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/catalog", status_code=302)

    except Exception as e:
        logger.error(f"[CALLBACK ERROR] {e}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=auth_failed")

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

# ==========================================================
#  CHECK AUTH STATUS (React uses this)
# ==========================================================
@router.get("/check")
async def check_auth(request: Request):
    session_cookie = request.cookies.get("session", "NO_COOKIE")
    user = request.session.get("user")

    logger.info("=== AUTH CHECK ===")
    logger.info(f"Cookie: {session_cookie[:20]}...")
    logger.info(f"Session: {dict(request.session)}")
    logger.info(f"User exists: {user is not None}")
    logger.info("===================")

    if user:
        return {"authenticated": True, "user": user}

    return {"authenticated": False}


# ==========================================================
#  LOGOUT
# ==========================================================
@router.post("/logout")
async def logout(request: Request):
    """
    Clear session + remove cookie + return W3 logout URL.
    """
    W3_LOGOUT = "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout"

    try:
        # Clear server-side session
        request.session.clear()

        response = JSONResponse(
            content={
                "message": "Logged out",
                "logout_url": W3_LOGOUT
            }
        )

        # Delete cookie
        response.set_cookie(
            key="session",
            value="",
            httponly=True,
            secure=True,
            samesite="none",
            max_age=0,
            expires=0,
        )

        logger.info("[LOGOUT] session cleared")
        return response

    except Exception as e:
        logger.error(f"[LOGOUT ERROR] {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Logout failed"})


# ==========================================================
#  VALIDATE USER SESSION
# ==========================================================
@router.get("/validate")
async def validate_session(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    return {
        "valid": True,
        "user": {
            "email": user.get("email"),
            "name": user.get("name"),
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
