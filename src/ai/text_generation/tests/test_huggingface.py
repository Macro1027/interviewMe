"""
Unit tests for Hugging Face text generation integration.

This file contains tests for generating text using the Hugging Face API.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.ai.text_generation.text_generation import TextGenerationService


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp.ClientSession for async tests."""
    with patch('aiohttp.ClientSession') as mock_session:
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[{
            'generated_text': 'This is a test response from Hugging Face API'
        }])
        mock_response.__aenter__.return_value = mock_response
        
        # Setup mock session post
        mock_session_instance = MagicMock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        yield mock_session


@pytest.fixture
def text_generation_service():
    """Create a TextGenerationService with mocked API key."""
    with patch('src.utils.config.get_settings') as mock_settings:
        mock_settings.return_value.HUGGINGFACE_API_KEY = "mock-api-key"
        mock_settings.return_value.HUGGINGFACE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        mock_settings.return_value.LLM_PROVIDER = "huggingface"
        
        service = TextGenerationService(api_key="mock-api-key", provider="huggingface")
        yield service


class TestHuggingFaceTextGeneration:
    """Tests for Hugging Face text generation."""
    
    async def test_generate_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a simple text completion."""
        # Call the method
        result = await text_generation_service.generate_completion(
            prompt="Generate a test response",
            max_tokens=100
        )
        
        # Verify result
        assert result == "This is a test response from Hugging Face API"
        
        # Verify the API was called with expected parameters
        mock_session = mock_aiohttp_session.return_value.__aenter__.return_value
        call_args = mock_session.post.call_args
        
        # First arg is URL
        url = call_args[0][0]
        assert "mistralai/Mixtral-8x7B-Instruct-v0.1" in url
        
        # Check payload
        payload = call_args[1]['json']
        assert "Generate a test response" in payload['inputs']
        assert payload['parameters']['max_new_tokens'] == 100
        assert payload['parameters']['return_full_text'] is False
        
        # Check headers
        headers = call_args[1]['headers']
        assert headers['Authorization'] == "Bearer mock-api-key"
    
    async def test_generate_chat_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a chat completion with multiple messages."""
        # Test data
        messages = [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": "Tell me about Python."},
            {"role": "assistant", "content": "Python is a programming language."},
            {"role": "user", "content": "What are its key features?"}
        ]
        
        # Call the method
        result = await text_generation_service.generate_chat_completion(
            messages=messages,
            max_tokens=200
        )
        
        # Verify result
        assert result == "This is a test response from Hugging Face API"
        
        # Verify the API was called with expected parameters
        mock_session = mock_aiohttp_session.return_value.__aenter__.return_value
        call_args = mock_session.post.call_args
        
        # Check URL
        url = call_args[0][0]
        assert "mistralai/Mixtral-8x7B-Instruct-v0.1" in url
        
        # Check payload
        payload = call_args[1]['json']
        # Verify that all messages were combined into the prompt
        assert "You are an AI assistant." in payload['inputs']
        assert "Tell me about Python." in payload['inputs']
        assert "Python is a programming language." in payload['inputs']
        assert "What are its key features?" in payload['inputs']
        
        # Check generation parameters
        assert payload['parameters']['max_new_tokens'] == 200
    
    async def test_api_error_handling(self, text_generation_service):
        """Test error handling for API failures."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock response for error
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.text = AsyncMock(return_value="Invalid request")
            mock_response.__aenter__.return_value = mock_response
            
            # Setup mock session post
            mock_session_instance = MagicMock()
            mock_session_instance.post.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Call the method and expect exception
            with pytest.raises(Exception) as excinfo:
                await text_generation_service.generate_completion(
                    prompt="Generate a test response",
                    max_tokens=100
                )
            
            # Verify exception details
            assert "Hugging Face API returned error: 400" in str(excinfo.value)
    
    async def test_fallback_to_perplexity(self, text_generation_service):
        """Test fallback to Perplexity when Hugging Face fails."""
        # First mock Hugging Face request to fail
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock response for error
            mock_response = AsyncMock()
            mock_response.status = 503  # Service unavailable
            mock_response.text = AsyncMock(return_value="Service unavailable")
            mock_response.__aenter__.return_value = mock_response
            
            # Setup mock session post
            mock_session_instance = MagicMock()
            mock_session_instance.post.return_value = mock_response
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Now mock the retry with Perplexity API to succeed
            with patch.object(
                text_generation_service, 
                '_generate_perplexity_chat_completion',
                new_callable=AsyncMock
            ) as mock_perplexity:
                # Setup mock successful response from Perplexity
                mock_perplexity.return_value = "Fallback response from Perplexity"
                
                # Call method with fallback enabled
                result = await text_generation_service.generate_completion(
                    prompt="Generate a test response",
                    max_tokens=100,
                    use_fallback=True
                )
                
                # Verify result is from fallback
                assert result == "Fallback response from Perplexity"
                
                # Verify fallback was called with expected parameters
                mock_perplexity.assert_called_once()
                call_args = mock_perplexity.call_args[1]
                assert call_args['messages'][0]['content'] == "Generate a test response" 