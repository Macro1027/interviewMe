#!/usr/bin/env python
"""
Example script demonstrating how to use the Perplexity API service.

This script shows how to generate completions and chat responses using 
the Perplexity service through the factory pattern.

Usage:
    python -m src.ai.examples.perplexity_example

Make sure to set the PERPLEXITY_API_KEY environment variable before running.
"""
import asyncio
import os
import sys

# Add project root to Python path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.ai.factory import get_completion_service
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger("perplexity_example")


async def test_completion():
    """Test the text completion functionality."""
    logger.info("Testing Perplexity text completion...")
    
    # Get the configured completion service (Perplexity)
    service = get_completion_service(provider="perplexity")
    
    # Generate a completion
    prompt = "Generate a technical interview question about Python generators:"
    response = await service.generate_completion(
        prompt=prompt,
        max_tokens=200,
        temperature=0.7
    )
    
    logger.info(f"Prompt: {prompt}")
    logger.info(f"Generated completion: {response}")
    return response


async def test_chat_completion():
    """Test the chat completion functionality."""
    logger.info("Testing Perplexity chat completion...")
    
    # Get the configured completion service (Perplexity)
    service = get_completion_service(provider="perplexity")
    
    # Prepare chat messages
    messages = [
        {"role": "system", "content": "You are an expert technical interviewer specialized in software engineering roles."},
        {"role": "user", "content": "I need a challenging question about microservices architecture and its testing strategies."}
    ]
    
    # Generate a chat completion
    response = await service.generate_chat_completion(
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    
    logger.info(f"Messages: {messages}")
    logger.info(f"Generated chat response: {response}")
    return response


async def main():
    """Run all examples."""
    try:
        # Check if API key is set
        from src.utils.config import get_settings
        settings = get_settings()
        
        if not settings.PERPLEXITY_API_KEY:
            logger.error("PERPLEXITY_API_KEY environment variable is not set.")
            logger.error("Please set this variable before running the example.")
            return
        
        # Run the examples
        await test_completion()
        print("\n" + "-" * 50 + "\n")
        await test_chat_completion()
        
    except Exception as e:
        logger.error(f"Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 