

# -------------------------
# app/api/v1/endpoints/auth.py
# -------------------------
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict
import logging
from app.bluegroups_auth import is_user_in_group
from app.config import settings
from app.auth.dependencies import get_current_active_user, get_current_user
from app.auth.permissions import get_user_roles

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login")
async def login(request: Request):
    """
    Start IBM AppID login flow.
    Always clear old session to avoid STATE MISMATCH errors.
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


@router.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        logger.info("[CALLBACK] Processing...")

        from app.main import oauth

        # IMPORTANT: remove any previous _state_appid keys BEFORE calling authorize_access_token
        # Authlib may re-populate state during the callback; removing stale keys avoids mismatch.
        for key in list(request.session.keys()):
            if key.startswith("_state_appid"):
                del request.session[key]

        # Exchange code for token
        token = await oauth.appid.authorize_access_token(request)
        logger.info("[CALLBACK] Token OK")

        # Parse user info
        try:
            user = await oauth.appid.parse_id_token(request, token)
        except Exception:
            logger.warning("[CALLBACK] ID token parse failed → using userinfo()")
            user = await oauth.appid.userinfo(token=token)

        email = user.get("email")
        name = user.get("name") or f"{user.get('given_name','')} {user.get('family_name','')}".strip()

        # Mark every user as admin (per your request). Replace with real group checks as needed.
        roles = ["admin"]

        # Save user + token in session
        request.session["user"] = {
            "sub": user.get("sub"),
            "name": name,
            "email": email,
            "given_name": user.get("given_name"),
            "family_name": user.get("family_name"),
            "identities": user.get("identities"),
            "roles": roles,
        }

        request.session["token"] = {
            "access_token": token.get("access_token"),
            "token_type": token.get("token_type"),
            "expires_at": token.get("expires_at"),
            "id_token": token.get("id_token"),
        }

        # Ensure session is flagged as modified so Starlette will write cookie
        try:
            request.session.modified = True
        except Exception:
            # Fallback for older starlette versions
            request.session.update(request.session)

        logger.info(f"[CALLBACK] Session saved for {email}")

        # Redirect back to frontend (cookie will be set by middleware on response)
        response = RedirectResponse(f"{settings.FRONTEND_URL}/catalog")
        return response

    except Exception as e:
        logger.error(f"[CALLBACK ERROR] {e}", exc_info=True)
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=auth_failed")


@router.get("/check")
async def check_auth(request: Request):
    session_cookie = request.cookies.get("session", "no_cookie...")
    user = request.session.get("user")

    logger.info("=== AUTH CHECK ===")
    logger.info(f"Cookie: {session_cookie[:20]}...")
    logger.info(f"Session keys: {list(request.session.keys())}")
    logger.info(f"User exists: {user is not None}")
    logger.info("===================")

    if user:
        return {"authenticated": True, "user": user}

    return {"authenticated": False}


@router.post("/logout")
async def logout(request: Request):
    W3_LOGOUT = "https://preprod.login.w3.ibm.com/idaas/mtfim/sps/idaas/logout"
    try:
        request.session.clear()
        response = JSONResponse(content={"message": "Logged out", "logout_url": W3_LOGOUT})
        # Explicitly clear cookie (middleware may also remove it)
        response.set_cookie(key="session", value="", httponly=True, max_age=0, expires=0, path='/', samesite='None')
        logger.info("[LOGOUT] session cleared")
        return response
    except Exception as e:
        logger.error(f"[LOGOUT ERROR] {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Logout failed"})

# End of file
