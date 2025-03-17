"""
Configuration loader for the AI Interview Simulation Platform.
This module handles loading environment variables and provides configuration
for the different components of the application.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from dotenv import load_dotenv
from pydantic import BaseSettings, validator, AnyHttpUrl, PostgresDsn, RedisDsn, field_validator
from loguru import logger


# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_ENV: str = "development"
    APP_NAME: str = "AI Interview Simulation Platform"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str
    JWT_SECRET: str
    TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS settings
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string to list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_URI: Optional[PostgresDsn] = None
    
    @validator("POSTGRES_URI", pre=True)
    def assemble_postgres_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Build Postgres URI from components if not already provided."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URI: Optional[RedisDsn] = None
    
    @validator("REDIS_URI", pre=True)
    def assemble_redis_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Build Redis URI from components if not already provided."""
        if isinstance(v, str):
            return v
        
        # Build Redis URI with or without password
        if values.get("REDIS_PASSWORD"):
            return f"redis://:{values.get('REDIS_PASSWORD')}@{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}"
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}"
    
    # AI Services
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ORGANIZATION: Optional[str] = None
    
    # Mock Settings
    MOCK_AI_SERVICES: bool = False
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    
    # Performance and Scaling
    MAX_WORKERS: int = 1
    WORKER_CONCURRENCY: int = 10
    RATE_LIMIT_PER_MINUTE: int = 60
    CONNECTION_POOL_SIZE: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    class Config:
        """Configuration for the settings class."""
        env_file = os.path.join(BASE_DIR, ".env")
        case_sensitive = True


def load_env_file(env_name: str = None) -> None:
    """
    Load the appropriate .env file based on the environment.
    
    Args:
        env_name: The environment name. If not provided, will try to read from APP_ENV
                 environment variable, defaulting to "development".
    """
    if not env_name:
        env_name = os.getenv("APP_ENV", "development")
    
    env_file = f".env.{env_name}" if env_name != "development" else ".env"
    env_path = os.path.join(BASE_DIR, env_file)
    
    if os.path.exists(env_path):
        logger.info(f"Loading environment from {env_file}")
        load_dotenv(env_path)
    else:
        logger.warning(f"Environment file {env_file} not found, using .env")
        load_dotenv(os.path.join(BASE_DIR, ".env"))


# Load environment variables before initializing settings
load_env_file()

# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings."""
    return settings 