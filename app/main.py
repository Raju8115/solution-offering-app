from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from app.config import settings
from app.api.v1.api import api_router
import logging
import os
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# from starlette.middleware.proxy_headers import ProxyHeadersMiddleware

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# App
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ----------------------------------------------------------------------
# 1️⃣ CORS FIRST (must be before session middleware)
# ----------------------------------------------------------------------
# app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://solution-offering-app.onrender.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="session",
    same_site="none",
    https_only=True,     # enables Secure
    max_age=86400,
    domain="solution-offering-app.onrender.com",
)

# ----------------------------------------------------------------------
# 3️⃣ OAuth config
# ----------------------------------------------------------------------
oauth = OAuth()
oauth.register(
    name="appid",
    client_id=settings.IBM_CLIENT_ID,
    client_secret=settings.IBM_CLIENT_SECRET,
    server_metadata_url=settings.IBM_DISCOVERY_ENDPOINT,
    client_kwargs={"scope": "openid email profile"},
)

# ----------------------------------------------------------------------
# 4️⃣ API Router
# ----------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# ----------------------------------------------------------------------
# 5️⃣ React static files
# ----------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/{full_path:path}")
async def spa(full_path: str):
    return FileResponse(os.path.join("frontend", "build", "index.html"))

# ----------------------------------------------------------------------
# Startup
# ----------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info("Solution Offering App - Starting")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")

    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://solution-offering-app.onrender.com",
    ]

    logger.info(f"CORS Allowed Origins: {ALLOWED_ORIGINS}")
    logger.info("=" * 70)


@app.get("/")
async def index():
    return {"message": "Solution Offering API running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/debug")
async def debug(request: Request):
    return {"cookies": request.cookies, "session": dict(request.session)}
