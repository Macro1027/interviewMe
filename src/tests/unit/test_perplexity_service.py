"""
Unit tests for the Perplexity service.
"""
import json
import pytest
from unittest import mock

import aiohttp
from aiohttp.client_reqrep import ClientResponse

from src.ai.perplexity_service import PerplexityService


class TestPerplexityService:
    """Tests for the PerplexityService class."""
    
    def setup_method(self):
        """Set up test method."""
        self.mock_api_key = "test_api_key"
        self.service = PerplexityService(api_key=self.mock_api_key)
    
    def test_init(self):
        """Test initialization."""
        assert self.service.api_key == self.mock_api_key
        assert self.service.api_base_url == "https://api.perplexity.ai"
        assert self.service.default_model == "pplx-70b-online"
    
    @pytest.mark.asyncio
    async def test_generate_completion(self):
        """Test generate_completion method."""
        # Mock the generate_chat_completion method
        with mock.patch.object(
            self.service, 'generate_chat_completion', 
            return_value="Test completion response"
        ) as mock_chat:
            result = await self.service.generate_completion(
                prompt="Test prompt", 
                max_tokens=100
            )
            
            # Verify the result
            assert result == "Test completion response"
            
            # Verify generate_chat_completion was called with correct args
            mock_chat.assert_called_once()
            args, kwargs = mock_chat.call_args
            assert kwargs['messages'] == [{"role": "user", "content": "Test prompt"}]
            assert kwargs['max_tokens'] == 100
    
    @pytest.mark.asyncio
    async def test_generate_chat_completion_success(self):
        """Test generate_chat_completion method with successful response."""
        # Mock response data
        mock_response_data = {
            "id": "test-response-id",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response"
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        
        # Create a mock for ClientResponse
        mock_response = mock.MagicMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json.return_value = mock_response_data
        
        # Create a mock for ClientSession
        mock_session = mock.MagicMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Mock aiohttp.ClientSession
        with mock.patch('aiohttp.ClientSession', return_value=mock_session):
            result = await self.service.generate_chat_completion(
                messages=[
                    {"role": "user", "content": "Test message"}
                ],
                max_tokens=100
            )
            
            # Verify the result
            assert result == "This is a test response"
            
            # Verify the request was made with correct parameters
            mock_session.post.assert_called_once()
            args, kwargs = mock_session.post.call_args
            assert args[0] == "https://api.perplexity.ai/chat/completions"
            assert kwargs['headers'] == {
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json"
            }
            assert json.loads(kwargs['json']['messages'][0]['content']) == "Test message"
            assert kwargs['json']['max_tokens'] == 100
    
    @pytest.mark.asyncio
    async def test_generate_chat_completion_error(self):
        """Test generate_chat_completion method with error response."""
        # Create a mock for ClientResponse
        mock_response = mock.MagicMock(spec=ClientResponse)
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        
        # Create a mock for ClientSession
        mock_session = mock.MagicMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        # Mock aiohttp.ClientSession
        with mock.patch('aiohttp.ClientSession', return_value=mock_session):
            with pytest.raises(Exception) as exc_info:
                await self.service.generate_chat_completion(
                    messages=[
                        {"role": "user", "content": "Test message"}
                    ],
                    max_tokens=100
                )
            
            assert "Perplexity API returned error: 400" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generate_chat_completion_network_error(self):
        """Test generate_chat_completion method with network error."""
        # Mock aiohttp.ClientSession to raise an exception
        with mock.patch('aiohttp.ClientSession', side_effect=aiohttp.ClientError("Network error")):
            with pytest.raises(Exception) as exc_info:
                await self.service.generate_chat_completion(
                    messages=[
                        {"role": "user", "content": "Test message"}
                    ],
                    max_tokens=100
                )
            
            assert "Perplexity API request failed" in str(exc_info.value)
    
    def test_count_tokens(self):
        """Test the count_tokens method."""
        # Test with various text inputs
        assert self.service.count_tokens("") == 1
        assert self.service.count_tokens("Hello, world!") == 4  # 13 chars / 4 + 1
        assert self.service.count_tokens("A" * 100) == 26  # 100 chars / 4 + 1 