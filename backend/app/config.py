from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Healthcare Appointment Manager"
    APP_ENV: Literal["development", "testing", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def fix_asyncpg_url(cls, v: str) -> str:
        """Fix database URLs for asyncpg compatibility."""
        if not v:
            return v
        # asyncpg requires postgresql:// instead of postgres://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        
        # asyncpg doesn't support sslmode, it uses ssl
        if "?sslmode=" in v or "&sslmode=" in v:
            v = v.replace("sslmode=", "ssl=")
            
        # Ensure it uses the asyncpg driver
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        return v

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # Redis
    REDIS_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery & Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Integration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 3

    # Email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "Healthcare Appointment Manager"
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # Google Calendar
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Slot Configuration
    SLOT_HOLD_TTL_SECONDS: int = 600
    SLOT_GENERATION_DAYS_AHEAD: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Celery
    CELERY_BROKER_URL: str | None = None  # Falls back to REDIS_URL
    CELERY_RESULT_BACKEND: str | None = None  # Falls back to REDIS_URL
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_ALWAYS_EAGER: bool = False  # True in tests

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
