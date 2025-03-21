"""
Text Generation Service for the AI Interview Simulation Platform.

This module provides text generation capabilities using various LLM providers,
with the default being Perplexity API.
"""
from typing import Dict, List, Optional, Union, Any
import json
import aiohttp

from src.utils.config import get_settings
from src.utils.logger import setup_logger

# Initialize logger and settings
logger = setup_logger(__name__)
settings = get_settings()


class TextGenerationService:
    """
    Service for text generation using LLM providers (default: Perplexity API).
    
    This service provides methods for generating text completions and
    chat completions using LLM APIs.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "perplexity"):
        """
        Initialize the text generation service.
        
        Args:
            api_key: Optional API key override. If not provided, uses the key from environment variables.
            provider: The LLM provider to use ('perplexity', 'huggingface').
        """
        self.provider = provider.lower()
        
        # Select API configuration based on provider
        if self.provider == "perplexity":
            self.api_key = api_key or settings.PERPLEXITY_API_KEY
            self.api_base_url = "https://api.perplexity.ai"
            self.model = settings.PERPLEXITY_MODEL or "pplx-70b-online"
            
            if not self.api_key:
                logger.warning("No Perplexity API key provided. Text generation service will not work correctly.")
        elif self.provider == "huggingface":
            self.api_key = api_key or settings.HUGGINGFACE_API_KEY
            self.api_base_url = "https://api-inference.huggingface.co/models"
            self.model = settings.HUGGINGFACE_MODEL or "mistralai/Mixtral-8x7B-Instruct-v0.1"
            
            if not self.api_key:
                logger.warning("No Hugging Face API key provided. Text generation service will not work correctly.")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers are 'perplexity' and 'huggingface'.")
    
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
        if self.provider == "perplexity":
            return await self._generate_perplexity_chat_completion(messages, max_tokens, **kwargs)
        elif self.provider == "huggingface":
            return await self._generate_huggingface_chat_completion(messages, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _generate_perplexity_chat_completion(
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
    
    async def _generate_huggingface_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 1024, 
        **kwargs
    ) -> str:
        """
        Generate a chat completion using Hugging Face API.
        
        Args:
            messages: List of message objects (role, content)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
        """
        # Extract or use default model
        model = kwargs.pop("model", self.model)
        
        # Prepare the request
        url = f"{self.api_base_url}/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format messages for Hugging Face
        # Convert chat format to prompt text
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"<|system|>\n{content}\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n"
            else:
                prompt += f"{content}\n"
        
        # Add the final assistant prompt
        prompt += "<|assistant|>\n"
        
        # Prepare payload
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "return_full_text": False
            }
        }
        
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in ["api_key", "model"]:
                payload["parameters"][key] = value
        
        logger.debug(f"Sending request to Hugging Face API with model: {model}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Hugging Face API error: {response.status}, {error_text}")
                        raise Exception(f"Hugging Face API returned error: {response.status}, {error_text}")
                    
                    result = await response.json()
                    
                    # Extract the generated text from the response
                    try:
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                        else:
                            generated_text = result.get("generated_text", "")
                        
                        logger.debug("Successfully generated text from Hugging Face API")
                        return generated_text
                    except Exception as e:
                        logger.error(f"Error parsing Hugging Face API response: {e}, Response: {result}")
                        raise Exception(f"Failed to parse Hugging Face API response: {e}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Hugging Face API request failed: {e}")
            raise Exception(f"Hugging Face API request failed: {e}")
    
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


# Singleton instance for the text generation service
_text_generation_service = None


async def get_text_generation_service() -> TextGenerationService:
    """
    Get or create the text generation service singleton.
    
    Returns:
        A configured TextGenerationService instance.
    """
    global _text_generation_service
    
    if _text_generation_service is None:
        # Create service with default provider
        provider = settings.LLM_PROVIDER or "perplexity"
        _text_generation_service = TextGenerationService(provider=provider)
    
    return _text_generation_service


# Utility functions for interview-specific text generation tasks

async def generate_interview_question(topic: str, difficulty: str = "medium") -> str:
    """
    Generate an interview question on a specific topic with specified difficulty.
    
    Args:
        topic: The topic for the interview question (e.g., "Python", "Algorithms", "System Design")
        difficulty: The difficulty level ("easy", "medium", "hard")
        
    Returns:
        str: Generated interview question
    """
    service = await get_text_generation_service()
    
    prompt = (
        f"Generate a {difficulty} difficulty interview question about {topic}. "
        f"The question should be challenging but clear, and test the candidate's knowledge and problem-solving skills. "
        f"Include only the question, without any additional explanation or answer."
    )
    
    return await service.generate_completion(prompt, max_tokens=300)


async def evaluate_interview_answer(question: str, answer: str) -> Dict[str, Any]:
    """
    Evaluate a candidate's answer to an interview question.
    
    Args:
        question: The interview question that was asked
        answer: The candidate's answer to evaluate
        
    Returns:
        Dict[str, Any]: Evaluation results including score, feedback, and areas of improvement
    """
    service = await get_text_generation_service()
    
    prompt = (
        "You are an expert interviewer evaluating a candidate's response. "
        "Provide a detailed but concise evaluation of the answer based on accuracy, "
        "completeness, clarity, and depth of understanding.\n\n"
        f"Question: {question}\n\n"
        f"Candidate's Answer: {answer}\n\n"
        "Provide your evaluation in JSON format with the following fields:\n"
        "- score (0-10)\n"
        "- feedback (brief general feedback)\n"
        "- strengths (list of strong points)\n"
        "- weaknesses (list of areas for improvement)\n"
        "- suggestions (specific tips for improvement)"
    )
    
    response = await service.generate_completion(prompt, max_tokens=500)
    
    # Parse the JSON response
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse evaluation as JSON: {response}")
        # Return a basic structure if parsing fails
        return {
            "score": 5,
            "feedback": "Unable to parse detailed evaluation. The response was: " + response[:100] + "...",
            "strengths": [],
            "weaknesses": ["Unable to analyze properly"],
            "suggestions": ["Please try again or rephrase your answer"]
        }


async def generate_follow_up_question(question: str, answer: str) -> str:
    """
    Generate a follow-up question based on the candidate's answer.
    
    Args:
        question: The original interview question
        answer: The candidate's answer
        
    Returns:
        str: A follow-up question to probe deeper or clarify the candidate's understanding
    """
    service = await get_text_generation_service()
    
    prompt = (
        "You are an expert technical interviewer. Based on the candidate's answer to the previous question, "
        "generate a thoughtful follow-up question that probes deeper into the topic or explores "
        "related areas to better assess the candidate's knowledge and understanding.\n\n"
        f"Original Question: {question}\n\n"
        f"Candidate's Answer: {answer}\n\n"
        "Generate only the follow-up question without any additional comments or explanations."
    )
    
    return await service.generate_completion(prompt, max_tokens=200) 