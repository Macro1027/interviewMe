"""
Unit tests for the Hugging Face implementation of the text generation service.
"""

import json
import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch

# Import the service to test
import sys
from pathlib import Path

# Add the parent directory to sys.path to import the module properly
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from text_generation import TextGenerationService


@pytest.fixture
async def mock_aiohttp_session():
    """Mock aiohttp ClientSession for testing."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = [{"generated_text": "This is a test response from Hugging Face API"}]
    mock_response.text.return_value = "Test response"
    
    mock_session = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        yield mock_session


@pytest.fixture
def text_generation_service():
    """Create a TextGenerationService instance for testing."""
    service = TextGenerationService(
        api_key="mock-api-key",
        provider="huggingface",
        model="mistralai/Mixtral-8x7B-Instruct-v0.1"
    )
    return service


class TestHuggingFaceTextGeneration:
    """Tests for the Hugging Face text generation implementation."""
    
    @pytest.mark.asyncio
    async def test_generate_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a text completion."""
        result = await text_generation_service.generate_completion("What is a RESTful API?")
        
        # Check the API call parameters
        mock_aiohttp_session.post.assert_called_once()
        args, kwargs = mock_aiohttp_session.post.call_args
        
        # The URL should include the model name
        assert "mistralai/Mixtral-8x7B-Instruct-v0.1" in args[0]
        
        # Check the payload
        assert kwargs["json"]["inputs"] == "What is a RESTful API?"
        assert "temperature" in kwargs["json"]["parameters"]
        assert "max_new_tokens" in kwargs["json"]["parameters"]
        
        # Check the result
        assert result == "This is a test response from Hugging Face API"
    
    @pytest.mark.asyncio
    async def test_generate_chat_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a chat completion."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is a RESTful API?"}
        ]
        
        result = await text_generation_service.generate_chat_completion(messages)
        
        # Check the API call parameters
        mock_aiohttp_session.post.assert_called_once()
        args, kwargs = mock_aiohttp_session.post.call_args
        
        # The URL should include the model name
        assert "mistralai/Mixtral-8x7B-Instruct-v0.1" in args[0]
        
        # Check that the payload includes the formatted messages
        assert "<|system|>" in kwargs["json"]["inputs"]
        assert "<|user|>" in kwargs["json"]["inputs"]
        assert "<|assistant|>" in kwargs["json"]["inputs"]
        assert "You are a helpful assistant" in kwargs["json"]["inputs"]
        assert "What is a RESTful API?" in kwargs["json"]["inputs"]
        
        # Check the result
        assert result == "This is a test response from Hugging Face API"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, text_generation_service):
        """Test error handling for API failures."""
        # Create a mock for error response
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        
        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            with pytest.raises(Exception) as excinfo:
                await text_generation_service.generate_completion("What is a RESTful API?")
            
            assert "Hugging Face API error: 400" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_fallback_to_perplexity(self, text_generation_service):
        """Test fallback to Perplexity when Hugging Face fails."""
        # First make Hugging Face fail
        mock_error_response = AsyncMock()
        mock_error_response.status = 500
        mock_error_response.text.return_value = "Internal Server Error"
        
        # Then make Perplexity succeed
        mock_success_response = AsyncMock()
        mock_success_response.status = 200
        mock_success_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Fallback response from Perplexity"
                    }
                }
            ]
        }
        
        # Create a session that first returns the error response, then the success response
        mock_session = AsyncMock()
        mock_session.post.side_effect = [
            AsyncMock(__aenter__=AsyncMock(return_value=mock_error_response)),
            AsyncMock(__aenter__=AsyncMock(return_value=mock_success_response))
        ]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            # Mock the TextGenerationService._generate_perplexity_completion method
            with patch.object(
                TextGenerationService, 
                '_generate_perplexity_completion',
                return_value="Fallback response from Perplexity"
            ) as mock_perplexity:
                result = await text_generation_service.generate_completion("What is a RESTful API?")
                
                # Verify the fallback was called
                mock_perplexity.assert_called_once()
                
                # Check the result is from the fallback
                assert result == "Fallback response from Perplexity"
    
    @pytest.mark.asyncio
    async def test_different_model_parameters(self, text_generation_service, mock_aiohttp_session):
        """Test with different model parameters."""
        # Call with custom parameters
        await text_generation_service.generate_completion(
            "What is a RESTful API?",
            temperature=0.9,
            max_tokens=2000
        )
        
        # Check the custom parameters were used
        args, kwargs = mock_aiohttp_session.post.call_args
        assert kwargs["json"]["parameters"]["temperature"] == 0.9
        assert kwargs["json"]["parameters"]["max_new_tokens"] == 2000 