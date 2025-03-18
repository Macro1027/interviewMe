"""
Perplexity API service implementation for text completions.
"""
import json
from typing import Dict, List, Optional, Union, Any

import aiohttp
from src.ai.interfaces import ICompletionService
from src.utils.config import get_settings
from src.utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class PerplexityService(ICompletionService):
    """
    Implementation of ICompletionService using Perplexity API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity API service.
        
        Args:
            api_key: Optional API key override. If not provided, uses the key from environment variables.
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.PERPLEXITY_API_KEY
        
        if not self.api_key:
            logger.warning("No Perplexity API key provided. Service will not work correctly.")
        
        self.api_base_url = "https://api.perplexity.ai"
        self.default_model = "pplx-70b-online"  # Default model if not specified
    
    async def generate_completion(self, prompt: str, max_tokens: int = 1024, **kwargs) -> str:
        """
        Generate a text completion using Perplexity API.
        
        Args:
            prompt: The prompt to generate completion for
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            str: Generated text completion
            
        Raises:
            Exception: If the API request fails
        """
        # For Perplexity, we'll convert this to a chat completion with a single user message
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_chat_completion(messages, max_tokens, **kwargs)
    
    async def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1024, 
        **kwargs
    ) -> str:
        """
        Generate a chat completion using Perplexity API.
        
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
        model = kwargs.pop("model", self.default_model)
        
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
            
        Note:
            This is a rough estimation as Perplexity doesn't provide a token counting endpoint.
            We're using a simple approximation based on words and punctuation.
        """
        # Simple approximation: assume average of 4 characters per token
        # This is a rough estimate and will vary based on the model and text content
        return len(text) // 4 + 1 