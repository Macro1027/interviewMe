"""
AI services for the interview platform.

This module provides direct access to AI capabilities without using the factory pattern.
The implementation uses Perplexity for language model capabilities.
"""
from typing import Dict, List, Optional, Union, Any
import aiohttp

from src.utils.config import get_settings
from src.utils.logger import setup_logger

# Initialize logger and settings
logger = setup_logger(__name__)
settings = get_settings()


class LLMService:
    """
    Provides language model capabilities using Perplexity API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the language model service.
        
        Args:
            api_key: Optional API key override. If not provided, uses the key from environment variables.
        """
        self.api_key = api_key or settings.PERPLEXITY_API_KEY
        
        if not self.api_key:
            logger.warning("No Perplexity API key provided. LLM service will not work correctly.")
        
        self.api_base_url = "https://api.perplexity.ai"
        self.model = settings.PERPLEXITY_MODEL or "pplx-70b-online"
    
    async def generate_completion(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """
        Generate a text completion.
        
        Args:
            prompt: The prompt to generate completion for
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            str: Generated text completion
            
        Raises:
            Exception: If the API request fails
        """
        # Convert to a chat completion with a single user message
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_chat_completion(messages, max_tokens, **kwargs)
    
    async def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1024, 
        **kwargs
    ) -> str:
        """
        Generate a chat completion.
        
        Args:
            messages: List of message objects (role, content)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            str: Generated text as response to the chat
            
        Raises:
            Exception: If the API request fails
        """
        # Extract or use default model
        model = kwargs.pop("model", self.model)
        
        # Prepare the request
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Merge default parameters with provided kwargs
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in ["api_key", "messages", "model"]:
                payload[key] = value
        
        logger.debug(f"Sending request to Perplexity API with model: {model}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Perplexity API error: {response.status}, {error_text}")
                        raise Exception(f"Perplexity API returned error: {response.status}, {error_text}")
                    
                    result = await response.json()
                    
                    # Extract the generated text from the response
                    try:
                        generated_text = result["choices"][0]["message"]["content"]
                        logger.debug("Successfully generated text from Perplexity API")
                        return generated_text
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error parsing Perplexity API response: {e}, Response: {result}")
                        raise Exception(f"Failed to parse Perplexity API response: {e}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Perplexity API request failed: {e}")
            raise Exception(f"Perplexity API request failed: {e}")
    
    async def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in the given text.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            int: Estimated token count
        """
        # Simple approximation: assume average of 4 characters per token
        return len(text) // 4 + 1


# Singleton instance for the LLM service
_llm_service = None


def get_llm_service() -> LLMService:
    """
    Get the LLM service instance (singleton).
    
    Returns:
        LLMService: The LLM service instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# Placeholder functions for other AI services that will be implemented later
# These follow the same simplified pattern without using the factory

def get_speech_recognition_service():
    """
    Get the speech recognition service.
    This will be implemented with a specific provider later.
    """
    raise NotImplementedError("Speech recognition service not yet implemented")


def get_speech_synthesis_service():
    """
    Get the speech synthesis service.
    This will be implemented with a specific provider later.
    """
    raise NotImplementedError("Speech synthesis service not yet implemented")


def get_sentiment_analysis_service():
    """
    Get the sentiment analysis service.
    This will be implemented with a specific provider later.
    """
    raise NotImplementedError("Sentiment analysis service not yet implemented")


def get_embedding_service():
    """
    Get the embedding service.
    This will be implemented with a specific provider later.
    """
    raise NotImplementedError("Embedding service not yet implemented") 