"""
Configuration utilities for the application.
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl, validator
from dotenv import load_dotenv

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_env_file(env: str = None):
    """
    Load environment variables from .env file.
    
    Args:
        env: Environment name to load (e.g., 'development', 'test', 'production')
    """
    env = env or os.environ.get("APP_ENV", "development")
    
    # Try to load from .env.<env> file
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
    
    # Also load from .env file as fallback
    if os.path.exists(".env"):
        load_dotenv(".env", override=False)  # Don't override existing variables
        logger.info("Loaded environment variables from .env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_ENV: str = "development"
    APP_NAME: str = "AI Interview Simulation Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Security settings
    SECRET_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string to list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # PostgreSQL settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_URI: Optional[PostgresDsn] = None
    
    @validator("POSTGRES_URI", pre=True)
    def assemble_postgres_uri(cls, v, values):
        """Build PostgreSQL URI from individual components."""
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}"
        )
    
    # MongoDB settings
    MONGODB_URI: str
    MONGODB_DATABASE: str = "interview_platform"
    
    # Redis settings (optional)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URI: Optional[str] = None
    
    @validator("REDIS_URI", pre=True)
    def assemble_redis_uri(cls, v, values):
        """Build Redis URI from individual components."""
        if isinstance(v, str):
            return v
        
        if not values.get("REDIS_HOST"):
            return None
        
        password_part = f":{values.get('REDIS_PASSWORD')}@" if values.get("REDIS_PASSWORD") else ""
        
        return f"redis://{password_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT', '6379')}"
    
    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_ORGANIZATION: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Perplexity API settings
    PERPLEXITY_API_KEY: Optional[str] = None
    PERPLEXITY_MODEL: str = "pplx-70b-online"
    
    # AI Provider Selection - REMOVED
    # We now use directly implemented services without factory pattern
    
    class Config:
        """Configuration for the settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    Returns:
        Settings: Application settings
    """
    # Load environment variables
    load_env_file()
    
    # Create settings
    settings = Settings()
    
    logger.info(f"Loaded settings for environment: {settings.APP_ENV}")
    return settings 