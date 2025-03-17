"""
Common fixtures for tests.
This file contains fixtures that can be used across all test modules.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from dotenv import load_dotenv

from src.utils.config import Settings, get_settings


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """
    Load the test environment variables.
    This fixture runs automatically at the start of the test session.
    """
    # Check if we're running in CI
    if os.environ.get("CI"):
        # CI environment should already have test variables set
        return
    
    # For local development, load from .env.test
    env_file = Path(__file__).parent.parent.parent / ".env.test"
    if env_file.exists():
        load_dotenv(dotenv_path=str(env_file))
        print(f"Loaded test environment from {env_file}")
    else:
        print("Warning: .env.test file not found, using environment variables")
    
    # Ensure we're in test mode
    os.environ["APP_ENV"] = "test"
    os.environ["MOCK_AI_SERVICES"] = "true"


@pytest.fixture
def test_settings():
    """
    Create settings for testing with default test values.
    This overrides any real API keys or credentials with test values.
    """
    env_vars = {
        "APP_ENV": "test",
        "DEBUG": "true",
        "SECRET_KEY": "test_secret_key",
        "JWT_SECRET": "test_jwt_secret",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres",
        "POSTGRES_DB": "test_db",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "MONGODB_URI": "mongodb://localhost:27017/test_db",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "OPENAI_API_KEY": "sk-test-key",
        "MOCK_AI_SERVICES": "true"
    }
    
    with mock.patch.dict(os.environ, env_vars):
        yield get_settings()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    fd, path = tempfile.mkstemp()
    try:
        yield Path(path)
    finally:
        os.close(fd)
        os.unlink(path)


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with mock.patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a mock response from OpenAI API.",
                        "role": "assistant"
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ],
            "created": 1677825464,
            "id": "chatcmpl-test123",
            "model": "gpt-3.5-turbo-0613",
            "object": "chat.completion",
            "usage": {
                "completion_tokens": 10,
                "prompt_tokens": 20,
                "total_tokens": 30
            }
        }
        yield mock_create


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client."""
    with mock.patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_client:
        # Configure the mock
        mock_db = mock.MagicMock()
        mock_collection = mock.MagicMock()
        
        # Set up the chain of mocks
        mock_client.return_value.get_database.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_db.command.return_value = {"ok": 1}
        
        # Configure common MongoDB operations
        mock_collection.find_one.return_value = {"_id": "test_id", "data": "test_data"}
        mock_collection.find.return_value.to_list.return_value = [
            {"_id": "id1", "data": "data1"},
            {"_id": "id2", "data": "data2"}
        ]
        mock_collection.insert_one.return_value.inserted_id = "new_id"
        
        yield mock_client


@pytest.fixture
def mock_sqlalchemy_engine():
    """Mock SQLAlchemy engine and session."""
    with mock.patch("sqlalchemy.ext.asyncio.create_async_engine") as mock_engine:
        # Configure the mock
        mock_connection = mock.AsyncMock()
        mock_result = mock.AsyncMock()
        
        # Set up the chain of mocks
        mock_engine.return_value = mock_engine
        mock_engine.connect.return_value.__aenter__.return_value = mock_connection
        mock_connection.execute.return_value = mock_result
        mock_result.fetchone.return_value = [1]
        mock_result.fetchall.return_value = [[1], [2], [3]]
        
        yield mock_engine 