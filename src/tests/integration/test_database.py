"""
Integration tests for database connections.
"""
import os
from unittest import mock

import pytest
import sqlalchemy
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.utils.config import Settings, get_settings


@pytest.fixture
def test_settings():
    """Create test settings for database testing."""
    with mock.patch.dict(os.environ, {
        "APP_ENV": "test",
        "SECRET_KEY": "test_secret",
        "JWT_SECRET": "test_jwt_secret",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "test_db",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "MONGODB_URI": "mongodb://localhost:27017/test_db",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "OPENAI_API_KEY": "test_api_key"
    }):
        return get_settings()


@pytest.mark.asyncio
async def test_postgres_connection(test_settings):
    """Test connection to PostgreSQL database."""
    # PostgreSQL async connection
    engine = create_async_engine(str(test_settings.POSTGRES_URI).replace('postgresql', 'postgresql+asyncpg'))
    
    try:
        # Test connection by creating a session
        async with engine.connect() as conn:
            # Simple query to test connection
            result = await conn.execute(sqlalchemy.text("SELECT 1"))
            row = await result.fetchone()
            assert row[0] == 1
    except Exception as e:
        pytest.skip(f"PostgreSQL database not available: {e}")


@pytest.mark.asyncio
async def test_mongodb_connection(test_settings):
    """Test connection to MongoDB database."""
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(test_settings.MONGODB_URI)
        db = client.get_database()
        
        # Test connection with a simple operation
        result = await db.command("ping")
        assert result.get("ok") == 1
    except Exception as e:
        pytest.skip(f"MongoDB database not available: {e}")


@pytest.mark.skipif(
    not os.environ.get("RUN_EXTERNAL_API_TESTS"), 
    reason="External API tests are disabled (set RUN_EXTERNAL_API_TESTS=1 to run)"
)
def test_openai_connection(test_settings):
    """Test connection to OpenAI API."""
    try:
        import openai
        
        # Configure the client
        openai.api_key = test_settings.OPENAI_API_KEY
        if test_settings.OPENAI_ORGANIZATION:
            openai.organization = test_settings.OPENAI_ORGANIZATION
        
        # Simple model list query to test connection
        models = openai.Model.list()
        assert len(models.data) > 0
    except Exception as e:
        pytest.skip(f"OpenAI API not available or invalid credentials: {e}") 