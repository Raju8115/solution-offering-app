from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # IBM AppID
    IBM_CLIENT_ID: str
    IBM_TENANT_ID: str
    IBM_CLIENT_SECRET: str
    IBM_OAUTH_SERVER_URL: str
    IBM_DISCOVERY_ENDPOINT: str
    IBM_PROFILES_URL: str | None = None   # 👈 Add this line
    
    # Application
    PROJECT_NAME: str = "Solution Offering API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Session
    SESSION_SECRET: str

    # Groups
    ADMIN_BLUEGROUP: str
    SOLUTION_ARCHITECT_BLUEGROUP: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()