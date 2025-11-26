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
# MIDDLEWARE ORDER MATTERS! Session must be added BEFORE CORS
# ----------------------------------------------------------------------

# 1. SESSION MIDDLEWARE FIRST
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="session",
    same_site="lax",  # Changed from "none" to "lax" for better compatibility
    max_age=86400,
    https_only=True,
)

# 2. CORS MIDDLEWARE SECOND
FRONTEND_ORIGIN = settings.FRONTEND_URL.rstrip('/')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "https://solution-offering-app.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# OAuth config
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
# API Router
# ----------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# ----------------------------------------------------------------------
# React static files
# ----------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/{path_name:path}")
async def spa_fallback(path_name: str):
    return FileResponse(os.path.join("frontend", "build", "index.html"))

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info(f"{settings.PROJECT_NAME} - Starting")
    logger.info(f"Frontend URL: {FRONTEND_ORIGIN}")
    logger.info("=" * 70)

@app.get("/")
async def index():
    return {"message": f"{settings.PROJECT_NAME} running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
