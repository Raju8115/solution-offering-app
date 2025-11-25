from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict
import logging

from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


# =========================================
#  LOGIN (START OIDC FLOW)
# =========================================
@router.get("/login")
async def login(request: Request):
    """
    Start IBM App ID OAuth2 Login Flow.
    """
    try:
        # 1) Clear old session to prevent state mismatch
        request.session.clear()

        # 2) Build callback URL
        redirect_uri = str(request.url_for("auth_callback"))
        logger.info(f"[LOGIN] redirect_uri: {redirect_uri}")

        # 3) Call AppID
        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)

    except Exception as e:
        logger.error(f"[LOGIN_ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login failed")


# =========================================
#  AUTH CALLBACK (AFTER LOGIN)
# =========================================
@router.get("/auth/callback")
async def auth_callback(request: Request):
    """
    Process App ID callback
    Exchange code → token → user info  
    Save user session  
    """
    try:
        logger.info("[CALLBACK] Processing callback...")

        from app.main import oauth

        # 1) Exchange code for access + id_token
        token = await oauth.appid.authorize_access_token(request)
        logger.info("[CALLBACK] Token exchange OK")

        # 2) Extract user information
        try:
            user = await oauth.appid.parse_id_token(request, token)
        except Exception:
            user = await oauth.appid.userinfo(token=token)

        # BASIC FIELDS
        email = user.get("email")
        name = user.get("name") or f"{user.get('given_name', '')} {user.get('family_name', '')}".strip()

        # =========================================
        #  3) EVERYONE IS ADMIN (as per requirement)
        # =========================================
        roles = ["admin"]

        # 4) Save session
        request.session["user"] = {
            "email": email,
            "name": name,
            "roles": roles,
        }

        request.session["token"] = token
        request.session.update(request.session)  # force save

        logger.info(f"[CALLBACK] Session saved for: {email}")

        # 5) Redirect to React app home (catalog)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/catalog", status_code=302)

    except Exception as e:
        logger.error(f"[CALLBACK_ERROR] {e}", exc_info=True)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?error=auth_failed")


# =========================================
#  GET USER PROFILE
# =========================================
@router.get("/user")
async def get_user(request: Request):
    user = request.session.get("user")

    if not user:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    return {"user": user}


# =========================================
#  CHECK AUTH STATUS
# =========================================
@router.get("/check")
async def check_auth(request: Request):
    session_cookie = request.cookies.get("session", "NO_SESSION_COOKIE")
    user = request.session.get("user")

    logger.info("=== AUTH CHECK START ===")
    logger.info(f"Cookie: {session_cookie[:20]}...")
    logger.info(f"Session: {dict(request.session)}")
    logger.info(f"User present: {user is not None}")
    logger.info("=== AUTH CHECK END ===")

    if user:
        return {"authenticated": True, "user": user}

    return {"authenticated": False}


# =========================================
#  LOGOUT
# =========================================
@router.post("/logout")
async def logout(request: Request):
    """
    Clear session + return W3 SAML logout URL
    """
    TRY_LOGOUT_URL = "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout"

    try:
        # Clear session state
        request.session.clear()

        # Build response
        response = JSONResponse(
            content={"message": "Logged out", "logout_url": TRY_LOGOUT_URL}
        )

        # Expire session cookie
        response.set_cookie(
            key="session",
            value="",
            httponly=True,
            secure=True,
            samesite="none",
            max_age=0,
            expires=0,
        )

        logger.info("[LOGOUT] Session cleared")
        return response

    except Exception as e:
        logger.error(f"[LOGOUT_ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": "Logout failed"})

