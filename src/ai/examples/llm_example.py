#!/usr/bin/env python
"""
Example script demonstrating how to use the consolidated LLM module.

This script shows how to generate completions, chat responses, and use
the higher-level utility functions for interview tasks.

Usage:
    python -m src.ai.examples.llm_example

Make sure to set the PERPLEXITY_API_KEY environment variable before running.
"""
import asyncio
import os
import sys

# Add project root to Python path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.ai.llm import (
    get_llm_service, 
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger("llm_example")


async def test_basic_completion():
    """Test the basic text completion functionality."""
    logger.info("Testing basic LLM text completion...")
    
    # Get the LLM service
    service = get_llm_service()
    
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
    logger.info("Testing LLM chat completion...")
    
    # Get the LLM service
    service = get_llm_service()
    
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


async def test_interview_utilities():
    """Test the higher-level interview utility functions."""
    logger.info("Testing interview utility functions...")
    
    # Generate an interview question
    topic = "Python concurrency"
    difficulty = "hard"
    question = await generate_interview_question(topic, difficulty)
    logger.info(f"Generated {difficulty} question about {topic}:")
    logger.info(question)
    
    # Simulate a candidate's answer (in a real scenario, this would come from the user)
    answer = (
        "Python offers several concurrency models. The threading module provides threads, but "
        "these are limited by the Global Interpreter Lock (GIL) which prevents true parallel execution "
        "of Python code. For I/O-bound tasks, asyncio offers event-driven concurrency with coroutines. "
        "For CPU-bound tasks, the multiprocessing module bypasses the GIL by creating separate processes. "
        "Each approach has its own use cases and trade-offs regarding memory usage, complexity, and performance."
    )
    logger.info(f"Simulated answer: {answer}")
    
    # Evaluate the answer
    evaluation = await evaluate_interview_answer(question, answer)
    logger.info("Evaluation of the answer:")
    logger.info(f"Score: {evaluation.get('score')}/10")
    logger.info(f"Feedback: {evaluation.get('feedback')}")
    logger.info(f"Strengths: {evaluation.get('strengths')}")
    logger.info(f"Weaknesses: {evaluation.get('weaknesses')}")
    
    # Generate a follow-up question
    follow_up = await generate_follow_up_question(question, answer)
    logger.info("Follow-up question:")
    logger.info(follow_up)
    
    return {
        "question": question,
        "answer": answer,
        "evaluation": evaluation,
        "follow_up": follow_up
    }


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
        
        # Run the basic examples
        await test_basic_completion()
        print("\n" + "-" * 50 + "\n")
        await test_chat_completion()
        print("\n" + "-" * 50 + "\n")
        
        # Run the interview utilities example
        await test_interview_utilities()
        
    except Exception as e:
        logger.error(f"Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 