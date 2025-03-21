"""
Text Generation Service for AI Interview Simulation Platform.

This module provides a unified interface for text generation using various
language model providers such as Perplexity and Hugging Face.
"""

import os
import json
import yaml
import logging
import aiohttp
import asyncio
from typing import Dict, List, Union, Optional, Any, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGenerationService:
    """A service for generating text using various language model providers."""

    def __init__(
        self, 
        api_key: str = None, 
        provider: str = "perplexity",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        config_path: str = None
    ):
        """
        Initialize the text generation service.
        
        Args:
            api_key: API key for the provider. If None, attempts to read from environment.
            provider: The provider to use ("perplexity" or "huggingface").
            model: The model to use. If None, uses the default from config.
            temperature: Controls randomness. Higher is more random.
            max_tokens: Maximum number of tokens to generate.
            config_path: Path to the config directory. If None, uses the default.
        """
        self.provider = provider.lower()
        
        # Load config
        if config_path is None:
            config_dir = Path(__file__).parent / "config"
        else:
            config_dir = Path(config_path)
        
        config_file = config_dir / f"{self.provider}.yaml"
        if not config_file.exists():
            raise ValueError(f"Config file not found: {config_file}")
        
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)
        
        # Set API key
        if api_key is None:
            env_var = f"{self.provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            if api_key is None:
                raise ValueError(f"API key not provided and {env_var} environment variable not set")
        self.api_key = api_key
        
        # Set model
        if model is None:
            model = self.config.get("default_model")
        self.model = model
        
        # Set generation parameters
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Session for API calls
        self._session = None
        
        logger.info(f"Initialized TextGenerationService with provider: {self.provider}, model: {self.model}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Generate a text completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for.
            **kwargs: Additional parameters to pass to the provider.
            
        Returns:
            Generated text completion.
        """
        try:
            if self.provider == "perplexity":
                return await self._generate_perplexity_completion(prompt, **kwargs)
            elif self.provider == "huggingface":
                return await self._generate_huggingface_completion(prompt, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            # Try fallback if primary provider fails
            if self.provider == "perplexity":
                logger.info("Falling back to Hugging Face")
                old_provider = self.provider
                self.provider = "huggingface"
                try:
                    result = await self._generate_huggingface_completion(prompt, **kwargs)
                    self.provider = old_provider
                    return result
                except Exception as fallback_error:
                    self.provider = old_provider
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            elif self.provider == "huggingface":
                logger.info("Falling back to Perplexity")
                old_provider = self.provider
                self.provider = "perplexity"
                try:
                    result = await self._generate_perplexity_completion(prompt, **kwargs)
                    self.provider = old_provider
                    return result
                except Exception as fallback_error:
                    self.provider = old_provider
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            raise

    async def generate_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat completion for the given messages.
        
        Args:
            messages: List of message objects with 'role' and 'content' keys.
            **kwargs: Additional parameters to pass to the provider.
            
        Returns:
            Generated chat completion.
        """
        try:
            if self.provider == "perplexity":
                return await self._generate_perplexity_chat(messages, **kwargs)
            elif self.provider == "huggingface":
                return await self._generate_huggingface_chat(messages, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Error generating chat completion: {e}")
            # Try fallback if primary provider fails
            if self.provider == "perplexity":
                logger.info("Falling back to Hugging Face")
                old_provider = self.provider
                self.provider = "huggingface"
                try:
                    result = await self._generate_huggingface_chat(messages, **kwargs)
                    self.provider = old_provider
                    return result
                except Exception as fallback_error:
                    self.provider = old_provider
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            elif self.provider == "huggingface":
                logger.info("Falling back to Perplexity")
                old_provider = self.provider
                self.provider = "perplexity"
                try:
                    result = await self._generate_perplexity_chat(messages, **kwargs)
                    self.provider = old_provider
                    return result
                except Exception as fallback_error:
                    self.provider = old_provider
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            raise

    async def _generate_perplexity_completion(self, prompt: str, **kwargs) -> str:
        """Generate a text completion using the Perplexity API."""
        session = await self._get_session()
        
        api_url = self.config.get("api_url", "https://api.perplexity.ai/chat/completions")
        
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Perplexity API error: {response.status} - {error_text}")
                
            result = await response.json()
            return result["choices"][0]["message"]["content"]

    async def _generate_perplexity_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion using the Perplexity API."""
        session = await self._get_session()
        
        api_url = self.config.get("api_url", "https://api.perplexity.ai/chat/completions")
        
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Perplexity API error: {response.status} - {error_text}")
                
            result = await response.json()
            return result["choices"][0]["message"]["content"]

    async def _generate_huggingface_completion(self, prompt: str, **kwargs) -> str:
        """Generate a text completion using the Hugging Face API."""
        session = await self._get_session()
        
        api_url = f"{self.config.get('api_url', 'https://api-inference.huggingface.co/models/')}{self.model}"
        
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with session.post(api_url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Hugging Face API error: {response.status} - {error_text}")
                
            result = await response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            return result.get("generated_text", "")

    async def _generate_huggingface_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a chat completion using the Hugging Face API."""
        # Format the messages for Hugging Face
        prompt = ""
        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"<|system|>\n{content}\n"
            elif role == "user":
                prompt += f"<|user|>\n{content}\n"
            elif role == "assistant":
                prompt += f"<|assistant|>\n{content}\n"
        
        prompt += "<|assistant|>\n"
        
        return await self._generate_huggingface_completion(prompt, **kwargs)


async def generate_interview_question(
    service: TextGenerationService,
    topic: str,
    difficulty: str = "medium"
) -> str:
    """
    Generate an interview question on a specific topic.
    
    Args:
        service: The TextGenerationService to use.
        topic: The topic for the interview question.
        difficulty: The difficulty level (easy, medium, hard).
        
    Returns:
        Generated interview question.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an expert interviewer. Generate a realistic and challenging interview question."
        },
        {
            "role": "user",
            "content": f"Create an interview question about {topic} at {difficulty} difficulty level. The question should assess the candidate's knowledge and problem-solving skills."
        }
    ]
    
    return await service.generate_chat_completion(messages)


async def evaluate_answer(
    service: TextGenerationService,
    question: str,
    answer: str,
    topic: str
) -> Dict[str, Any]:
    """
    Evaluate a candidate's answer to an interview question.
    
    Args:
        service: The TextGenerationService to use.
        question: The interview question.
        answer: The candidate's answer.
        topic: The topic area being assessed.
        
    Returns:
        Dictionary containing evaluation details.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an expert in evaluating interview responses. Provide a detailed and fair assessment."
        },
        {
            "role": "user",
            "content": f"""
            Question: {question}
            
            Candidate's Answer: {answer}
            
            Evaluate the candidate's answer to this {topic} question. Provide:
            1. A score from 1-10
            2. Specific feedback
            3. Key strengths
            4. Areas for improvement
            
            Format your response as a JSON object with fields: score, feedback, strengths, weaknesses.
            """
        }
    ]
    
    response = await service.generate_chat_completion(messages)
    
    try:
        # Try to parse JSON response
        evaluation = json.loads(response)
        return evaluation
    except json.JSONDecodeError:
        # Fallback to text-based response if JSON parsing fails
        logger.warning("Failed to parse JSON evaluation, returning raw text")
        return {
            "score": 0,
            "feedback": response,
            "strengths": [],
            "weaknesses": []
        }


async def generate_followup_question(
    service: TextGenerationService,
    original_question: str,
    answer: str,
    topic: str
) -> str:
    """
    Generate a follow-up question based on a candidate's answer.
    
    Args:
        service: The TextGenerationService to use.
        original_question: The original interview question.
        answer: The candidate's answer.
        topic: The topic area being assessed.
        
    Returns:
        A relevant follow-up question.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an expert interviewer. Generate a relevant follow-up question based on the candidate's response."
        },
        {
            "role": "user",
            "content": f"""
            Original Question: {original_question}
            
            Candidate's Answer: {answer}
            
            Based on this response about {topic}, what would be a good follow-up question that:
            1. Builds on something mentioned in their answer
            2. Probes deeper into their understanding
            3. Challenges them to think critically about the topic
            """
        }
    ]
    
    return await service.generate_chat_completion(messages)


# Practical usage example (for documentation purposes)
async def example_usage():
    """Example usage of the TextGenerationService."""
    # Initialize the service with environment variables
    service = TextGenerationService()
    
    try:
        # Generate a simple completion
        response = await service.generate_completion(
            "Explain what a RESTful API is in 3 sentences."
        )
        print(f"Completion response: {response}")
        
        # Generate a chat completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How can I prepare for a technical interview?"}
        ]
        
        chat_response = await service.generate_chat_completion(messages)
        print(f"Chat response: {chat_response}")
        
        # Generate an interview question
        question = await generate_interview_question(service, "Python Programming", "intermediate")
        print(f"Generated question: {question}")
        
        # Evaluate an answer
        sample_answer = "Python is an interpreted language. It uses dynamic typing and garbage collection."
        evaluation = await evaluate_answer(service, question, sample_answer, "Python")
        print(f"Evaluation: {evaluation}")
        
        # Generate a follow-up question
        followup = await generate_followup_question(service, question, sample_answer, "Python")
        print(f"Follow-up question: {followup}")
        
    finally:
        # Close the session
        await service.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage()) 