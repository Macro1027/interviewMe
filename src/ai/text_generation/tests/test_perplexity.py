"""
Unit tests for Perplexity text generation integration.

This file contains tests for generating text using the Perplexity API.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.ai.text_generation.text_generation import (
    TextGenerationService,
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp.ClientSession for async tests."""
    with patch('aiohttp.ClientSession') as mock_session:
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'choices': [{'message': {'content': 'This is a test response from Perplexity API'}}]
        })
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
        mock_settings.return_value.PERPLEXITY_API_KEY = "mock-api-key"
        mock_settings.return_value.PERPLEXITY_MODEL = "pplx-70b-online"
        mock_settings.return_value.LLM_PROVIDER = "perplexity"
        
        service = TextGenerationService(api_key="mock-api-key", provider="perplexity")
        yield service


class TestPerplexityTextGeneration:
    """Tests for Perplexity text generation."""
    
    async def test_generate_completion(self, text_generation_service, mock_aiohttp_session):
        """Test generating a simple text completion."""
        # Call the method
        result = await text_generation_service.generate_completion(
            prompt="Generate a test response",
            max_tokens=100
        )
        
        # Verify result
        assert result == "This is a test response from Perplexity API"
        
        # Verify the API was called with expected parameters
        mock_session = mock_aiohttp_session.return_value.__aenter__.return_value
        call_args = mock_session.post.call_args[1]
        
        # Check payload
        payload = call_args['json']
        assert payload['model'] == "pplx-70b-online"
        assert payload['max_tokens'] == 100
        assert len(payload['messages']) == 1
        assert payload['messages'][0]['role'] == "user"
        assert payload['messages'][0]['content'] == "Generate a test response"
        
        # Check headers
        headers = call_args['headers']
        assert headers['Authorization'] == "Bearer mock-api-key"
        assert headers['Content-Type'] == "application/json"
    
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
        assert result == "This is a test response from Perplexity API"
        
        # Verify the API was called with expected parameters
        mock_session = mock_aiohttp_session.return_value.__aenter__.return_value
        call_args = mock_session.post.call_args[1]
        
        # Check payload
        payload = call_args['json']
        assert payload['model'] == "pplx-70b-online"
        assert payload['max_tokens'] == 200
        assert len(payload['messages']) == 4
        assert payload['messages'] == messages
    
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
            assert "Perplexity API returned error: 400" in str(excinfo.value)


@pytest.fixture
def mock_text_generation_service():
    """Mock the text generation service for high-level function tests."""
    with patch('src.ai.text_generation.text_generation.get_text_generation_service') as mock_service_func:
        mock_service = AsyncMock()
        mock_service.generate_completion = AsyncMock(return_value="Mocked response")
        mock_service_func.return_value = mock_service
        yield mock_service


class TestInterviewFunctions:
    """Tests for interview-specific text generation functions."""
    
    async def test_generate_interview_question(self, mock_text_generation_service):
        """Test generating an interview question."""
        result = await generate_interview_question(topic="Python", difficulty="hard")
        
        assert result == "Mocked response"
        
        # Verify the service was called with expected parameters
        call_args = mock_text_generation_service.generate_completion.call_args
        prompt = call_args[1]['prompt']
        
        assert "Python" in prompt
        assert "hard difficulty" in prompt
        assert "interview question" in prompt
    
    async def test_evaluate_interview_answer(self, mock_text_generation_service):
        """Test evaluating an interview answer."""
        # Setup mock JSON response
        mock_text_generation_service.generate_completion.return_value = json.dumps({
            "score": 8,
            "feedback": "Good answer",
            "strengths": ["Clear explanation", "Good examples"],
            "weaknesses": ["Could be more concise"],
            "suggestions": ["Try to be more specific"]
        })
        
        result = await evaluate_interview_answer(
            question="What is Python?",
            answer="Python is a programming language"
        )
        
        assert result["score"] == 8
        assert result["feedback"] == "Good answer"
        assert len(result["strengths"]) == 2
        assert len(result["weaknesses"]) == 1
        assert len(result["suggestions"]) == 1
        
        # Verify the service was called with expected parameters
        call_args = mock_text_generation_service.generate_completion.call_args
        prompt = call_args[1]['prompt']
        
        assert "What is Python?" in prompt
        assert "Python is a programming language" in prompt
        assert "JSON" in prompt
    
    async def test_generate_follow_up_question(self, mock_text_generation_service):
        """Test generating a follow-up question."""
        result = await generate_follow_up_question(
            question="What is Python?",
            answer="Python is a programming language"
        )
        
        assert result == "Mocked response"
        
        # Verify the service was called with expected parameters
        call_args = mock_text_generation_service.generate_completion.call_args
        prompt = call_args[1]['prompt']
        
        assert "Original Question: What is Python?" in prompt
        assert "Candidate's Answer: Python is a programming language" in prompt
        assert "follow-up question" in prompt 