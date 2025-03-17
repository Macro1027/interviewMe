"""
Unit tests for the configuration module.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from dotenv import load_dotenv

from src.utils.config import Settings, load_env_file, get_settings


class TestSettings:
    """Tests for the Settings class."""

    def test_default_values(self):
        """Test that default values are correctly set."""
        # Mock environment to avoid loading .env file
        with mock.patch.dict(os.environ, {
            "SECRET_KEY": "test_secret",
            "JWT_SECRET": "test_jwt_secret",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "test_db",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "MONGODB_URI": "mongodb://localhost:27017/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "OPENAI_API_KEY": "test_api_key"
        }):
            settings = Settings()
            assert settings.APP_ENV == "development"
            assert settings.APP_NAME == "AI Interview Simulation Platform"
            assert settings.DEBUG is False
            assert settings.PORT == 8000
            assert settings.HOST == "0.0.0.0"
            assert settings.LOG_LEVEL == "INFO"
            assert settings.SECRET_KEY == "test_secret"
            assert settings.JWT_SECRET == "test_jwt_secret"
            assert settings.TOKEN_EXPIRE_MINUTES == 60

    def test_cors_origins_parsing(self):
        """Test that CORS origins are correctly parsed from a string."""
        with mock.patch.dict(os.environ, {
            "SECRET_KEY": "test_secret",
            "JWT_SECRET": "test_jwt_secret",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "test_db",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "MONGODB_URI": "mongodb://localhost:27017/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "OPENAI_API_KEY": "test_api_key",
            "CORS_ORIGINS": "http://localhost:3000,http://example.com"
        }):
            settings = Settings()
            assert len(settings.CORS_ORIGINS) == 2
            assert "http://localhost:3000" in settings.CORS_ORIGINS
            assert "http://example.com" in settings.CORS_ORIGINS


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as f:
        f.write("APP_ENV=test\n")
        f.write("DEBUG=true\n")
        f.write("SECRET_KEY=test_secret_key\n")
        f.write("JWT_SECRET=test_jwt_secret_key\n")
    yield path
    os.unlink(path)


class TestEnvLoading:
    """Tests for environment loading functions."""

    def test_load_env_file(self, temp_env_file):
        """Test loading environment from a file."""
        with mock.patch('os.path.join', return_value=temp_env_file):
            with mock.patch('os.path.exists', return_value=True):
                load_env_file('test')
                assert os.environ.get('APP_ENV') == 'test'
                assert os.environ.get('DEBUG') == 'true'

    def test_get_settings(self):
        """Test the get_settings function returns a Settings instance."""
        with mock.patch.dict(os.environ, {
            "SECRET_KEY": "test_secret",
            "JWT_SECRET": "test_jwt_secret",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "test_db",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "MONGODB_URI": "mongodb://localhost:27017/test",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": "6379",
            "OPENAI_API_KEY": "test_api_key"
        }):
            settings = get_settings()
            assert isinstance(settings, Settings)
            assert settings.SECRET_KEY == "test_secret" 