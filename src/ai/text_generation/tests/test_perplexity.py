"""
Unit tests for the Perplexity implementation of the text generation service.
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

from text_generation import TextGenerationService, generate_interview_question, evaluate_answer, generate_followup_question


@pytest.fixture
async def mock_aiohttp_session():
    """Mock aiohttp ClientSession for testing."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {
        "id": "test-id",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from Perplexity API"
                },
                "index": 0,
                "finish_reason": "stop"
            }
        ]
    }
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
        provider="perplexity",
        model="pplx-70b-online"
    )
    return service


class TestPerplexityTextGeneration:
    """Tests for the Perplexity text generation implementation."""
    
    @pytest.mark.asyncio
    async def test_generate_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a text completion."""
        result = await text_generation_service.generate_completion("What is a RESTful API?")
        
        # Check the API call parameters
        mock_aiohttp_session.post.assert_called_once()
        args, kwargs = mock_aiohttp_session.post.call_args
        
        assert args[0] == "https://api.perplexity.ai/chat/completions"
        assert kwargs["json"]["model"] == "pplx-70b-online"
        assert kwargs["json"]["messages"][0]["content"] == "What is a RESTful API?"
        assert kwargs["json"]["temperature"] == 0.7
        
        # Check the result
        assert result == "This is a test response from Perplexity API"
    
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
        
        assert args[0] == "https://api.perplexity.ai/chat/completions"
        assert kwargs["json"]["model"] == "pplx-70b-online"
        assert kwargs["json"]["messages"] == messages
        assert kwargs["json"]["temperature"] == 0.7
        
        # Check the result
        assert result == "This is a test response from Perplexity API"
    
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
            
            assert "Perplexity API error: 400" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_fallback_to_huggingface(self, text_generation_service):
        """Test fallback to Hugging Face when Perplexity fails."""
        # First make Perplexity fail
        mock_error_response = AsyncMock()
        mock_error_response.status = 500
        mock_error_response.text.return_value = "Internal Server Error"
        
        # Then make Hugging Face succeed
        mock_success_response = AsyncMock()
        mock_success_response.status = 200
        mock_success_response.json.return_value = [{"generated_text": "Fallback response from Hugging Face"}]
        
        # Create a session that first returns the error response, then the success response
        mock_session = AsyncMock()
        mock_session.post.side_effect = [
            AsyncMock(__aenter__=AsyncMock(return_value=mock_error_response)),
            AsyncMock(__aenter__=AsyncMock(return_value=mock_success_response))
        ]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            # Mock the TextGenerationService._generate_huggingface_completion method
            with patch.object(
                TextGenerationService, 
                '_generate_huggingface_completion',
                return_value="Fallback response from Hugging Face"
            ) as mock_huggingface:
                result = await text_generation_service.generate_completion("What is a RESTful API?")
                
                # Verify the fallback was called
                mock_huggingface.assert_called_once()
                
                # Check the result is from the fallback
                assert result == "Fallback response from Hugging Face"


@pytest.fixture
def mock_text_generation_service():
    """Create a mocked TextGenerationService for high-level function tests."""
    service = MagicMock()
    service.generate_chat_completion = AsyncMock(return_value="Test response")
    return service


class TestInterviewFunctions:
    """Tests for the interview-specific utility functions."""
    
    @pytest.mark.asyncio
    async def test_generate_interview_question(self, mock_text_generation_service):
        """Test generating an interview question."""
        result = await generate_interview_question(
            mock_text_generation_service,
            topic="Python Programming",
            difficulty="intermediate"
        )
        
        # Check that the service was called with the right parameters
        mock_text_generation_service.generate_chat_completion.assert_called_once()
        args, _ = mock_text_generation_service.generate_chat_completion.call_args
        
        # Check the messages content
        messages = args[0]
        assert any("expert interviewer" in msg["content"] for msg in messages)
        assert any("Python Programming" in msg["content"] for msg in messages)
        assert any("intermediate" in msg["content"] for msg in messages)
        
        # Check the result
        assert result == "Test response"
    
    @pytest.mark.asyncio
    async def test_evaluate_answer(self, mock_text_generation_service):
        """Test evaluating an answer."""
        # Mock the JSON response for evaluate_answer
        mock_text_generation_service.generate_chat_completion.return_value = json.dumps({
            "score": 8,
            "feedback": "Good answer, but could be more detailed.",
            "strengths": ["Clear explanation", "Correct concepts"],
            "weaknesses": ["Lacks depth", "Missing examples"]
        })
        
        result = await evaluate_answer(
            mock_text_generation_service,
            question="What is polymorphism in Python?",
            answer="Polymorphism is the ability of different classes to respond to the same method.",
            topic="Python OOP"
        )
        
        # Check that the service was called with the right parameters
        mock_text_generation_service.generate_chat_completion.assert_called_once()
        args, _ = mock_text_generation_service.generate_chat_completion.call_args
        
        # Check the messages content
        messages = args[0]
        assert any("evaluating interview responses" in msg["content"] for msg in messages)
        assert any("What is polymorphism in Python?" in msg["content"] for msg in messages)
        assert any("Polymorphism is the ability" in msg["content"] for msg in messages)
        
        # Check the result
        assert result["score"] == 8
        assert len(result["strengths"]) == 2
        assert len(result["weaknesses"]) == 2
    
    @pytest.mark.asyncio
    async def test_generate_followup_question(self, mock_text_generation_service):
        """Test generating a follow-up question."""
        result = await generate_followup_question(
            mock_text_generation_service,
            original_question="What is polymorphism in Python?",
            answer="Polymorphism is the ability of different classes to respond to the same method.",
            topic="Python OOP"
        )
        
        # Check that the service was called with the right parameters
        mock_text_generation_service.generate_chat_completion.assert_called_once()
        args, _ = mock_text_generation_service.generate_chat_completion.call_args
        
        # Check the messages content
        messages = args[0]
        assert any("follow-up question" in msg["content"] for msg in messages)
        assert any("What is polymorphism in Python?" in msg["content"] for msg in messages)
        assert any("Polymorphism is the ability" in msg["content"] for msg in messages)
        
        # Check the result
        assert result == "Test response" 