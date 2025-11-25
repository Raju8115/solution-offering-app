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
    Start OAuth2 login.
    Clear stale session to avoid 'state mismatch'.
    """
    try:
        request.session.clear()  # IMPORTANT

        redirect_uri = str(request.url_for("auth_callback"))
        logger.info(f"[LOGIN] redirect_uri = {redirect_uri}")

        from app.main import oauth
        return await oauth.appid.authorize_redirect(request, redirect_uri)

    except Exception as e:
        logger.error(f"[LOGIN ERROR] {e}", exc_info=True)
        raise HTTPException(500, "Login failed")


# ==========================================================
#  CALLBACK (after successful login)
# ==========================================================
@router.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        logger.info("[CALLBACK] Processing...")

        from app.main import oauth

        token = await oauth.appid.authorize_access_token(request)
        logger.info("[CALLBACK] Token OK")

        # Fetch user
        try:
            userinfo = await oauth.appid.parse_id_token(request, token)
        except:
            logger.warning("[CALLBACK] ID token parse failed → using userinfo()")
            userinfo = await oauth.appid.userinfo(token=token)

        email = userinfo.get("email")
        name = userinfo.get("name") or f"{userinfo.get('given_name','')} {userinfo.get('family_name','')}".strip()

        # ===================================================
        # REMOVE AppID internal state keys (MUST DO)
        # ===================================================
        for key in list(request.session.keys()):
            if key.startswith("_state_appid"):
                del request.session[key]

        # ===================================================
        # FORCE USER AS ADMIN
        # ===================================================
        roles = ["admin"]

        # ===================================================
        # SAVE SESSION (100% stable format)
        # ===================================================
        request.session["user"] = {
            "sub": userinfo.get("sub"),
            "email": email,
            "name": name,
            "given_name": userinfo.get("given_name"),
            "family_name": userinfo.get("family_name"),
            "identities": userinfo.get("identities"),
            "roles": roles,
        }

        request.session["token"] = {
            "access_token": token.get("access_token"),
            "token_type": token.get("token_type"),
            "expires_at": token.get("expires_at"),
            "id_token": token.get("id_token"),
        }

        request.session.update(request.session)  # FORCE SAVE

        logger.info(f"[CALLBACK] Session saved for {email}")
        logger.info(f"[CALLBACK] Redirect -> {settings.FRONTEND_URL}/catalog")

        return RedirectResponse(f"{settings.FRONTEND_URL}/catalog")

    except Exception as e:
        logger.error(f"[CALLBACK ERROR] {e}", exc_info=True)
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=auth_failed")


# ==========================================================
#  CHECK AUTH (called by React)
# ==========================================================
@router.get("/check")
async def check_auth(request: Request):
    """
    React uses this to verify authentication on page load.
    """
    user = request.session.get("user")

    session_id = request.cookies.get("session", "no_cookie")

    logger.info("=== AUTH CHECK ===")
    logger.info(f"Cookie: {session_id[:20]}...")
    logger.info(f"Session keys: {list(request.session.keys())}")
    logger.info(f"User exists: {bool(user)}")
    logger.info("==================")

    if user:
        return {"authenticated": True, "user": user}

    return {"authenticated": False}

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
#  LOGOUT
# ==========================================================
@router.post("/logout")
async def logout(request: Request):
    try:
        request.session.clear()

        W3_LOGOUT = "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout"

        resp = JSONResponse(
            {"message": "Logged out", "logout_url": W3_LOGOUT}
        )

        resp.set_cookie(
            "session",
            value="",
            secure=True,
            httponly=True,
            samesite="none",
            expires=0,
            max_age=0,
        )

        logger.info("[LOGOUT] Session cleared")
        return resp

    except Exception as e:
        logger.error(f"[LOGOUT ERROR] {e}", exc_info=True)
        return JSONResponse({"error": "Logout failed"}, status_code=500)


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

# roles = user.get("roles", [])
# if any(r in roles for r in allowed_groups):
#     return user
