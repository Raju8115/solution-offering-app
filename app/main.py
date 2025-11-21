from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from app.config import settings
from app.api.v1.api import api_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add Session Middleware (MUST be before CORS for cookies to work)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="session",
    max_age=3600,  # Session expires in 1 hour
    same_site="lax",  # "lax" works better for OAuth redirects
    https_only=False,  # Keep False for development
    domain=None,  # Let browser handle domain
)

# Configure CORS - IMPORTANT: Must allow credentials for sessions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OAuth with Authlib
oauth = OAuth()
oauth.register(
    name='appid',
    client_id=settings.IBM_CLIENT_ID,
    client_secret=settings.IBM_CLIENT_SECRET,
    server_metadata_url=settings.IBM_DISCOVERY_ENDPOINT,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 80)
    logger.info("APPLICATION STARTING")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"Client ID: {settings.IBM_CLIENT_ID}")
    logger.info(f"Discovery Endpoint: {settings.IBM_DISCOVERY_ENDPOINT}")
    logger.info("=" * 80)


@app.get("/")
async def root():
    return {
        "message": "Solution Offering API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/debug")
async def debug(request: Request):
    return {
        "cookies_sent": request.cookies,
        "session": request.session
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )