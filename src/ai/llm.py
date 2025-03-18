"""
Language Model (LLM) services for the interview platform.

This module provides direct access to LLM capabilities using Perplexity API.
All LLM functionality is consolidated in this single file.
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


# Utility functions for common LLM tasks
async def generate_interview_question(topic: str, difficulty: str = "medium") -> str:
    """
    Generate an interview question on a specific topic with specified difficulty.
    
    Args:
        topic: The topic for the interview question (e.g., "Python", "Algorithms", "System Design")
        difficulty: The difficulty level ("easy", "medium", "hard")
        
    Returns:
        str: Generated interview question
    """
    llm = get_llm_service()
    
    prompt = (
        f"Generate a {difficulty} difficulty interview question about {topic}. "
        f"The question should be challenging but clear, and test the candidate's knowledge and problem-solving skills. "
        f"Include only the question, without any additional explanation or answer."
    )
    
    return await llm.generate_completion(prompt, max_tokens=300)


async def evaluate_interview_answer(question: str, answer: str) -> Dict[str, Any]:
    """
    Evaluate a candidate's answer to an interview question.
    
    Args:
        question: The interview question that was asked
        answer: The candidate's answer to evaluate
        
    Returns:
        Dict[str, Any]: Evaluation results including score, feedback, and areas of improvement
    """
    llm = get_llm_service()
    
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
    
    response = await llm.generate_completion(prompt, max_tokens=500)
    
    # This is a simple implementation - in practice, you'd want to properly parse the JSON
    # and handle potential parsing errors
    import json
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
    llm = get_llm_service()
    
    prompt = (
        "You are an expert technical interviewer. Based on the candidate's answer to the previous question, "
        "generate a thoughtful follow-up question that probes deeper into the topic or explores "
        "related areas to better assess the candidate's knowledge and understanding.\n\n"
        f"Original Question: {question}\n\n"
        f"Candidate's Answer: {answer}\n\n"
        "Generate only the follow-up question without any additional comments or explanations."
    )
    
    return await llm.generate_completion(prompt, max_tokens=200) 