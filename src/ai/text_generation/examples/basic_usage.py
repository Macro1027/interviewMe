"""
Basic usage examples for the TextGenerationService.

This example demonstrates how to use the TextGenerationService for
generating text completions and chat-based interactions.

Usage:
    python -m src.ai.text_generation.examples.basic_usage
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from src.ai.text_generation import (
    TextGenerationService,
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)


async def basic_completion_example():
    """Example of basic text completion."""
    service = TextGenerationService()
    
    print("\n=== Basic Text Completion ===")
    prompt = "Explain what a RESTful API is in 3 sentences."
    
    print(f"Prompt: {prompt}")
    response = await service.generate_completion(prompt=prompt, max_tokens=150)
    print(f"Response: {response}")


async def chat_completion_example():
    """Example of chat-based completion."""
    service = TextGenerationService()
    
    print("\n=== Chat Completion ===")
    messages = [
        {"role": "system", "content": "You are a technical interviewer for a software engineering position."},
        {"role": "user", "content": "What questions should I ask to assess a candidate's knowledge of databases?"}
    ]
    
    print("Messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    
    response = await service.generate_chat_completion(messages=messages, max_tokens=200)
    print(f"Response: {response}")


async def interview_utility_examples():
    """Examples of interview-specific utility functions."""
    # Generate interview question
    print("\n=== Generate Interview Question ===")
    topic = "Python Programming"
    difficulty = "intermediate"
    
    print(f"Topic: {topic}, Difficulty: {difficulty}")
    question = await generate_interview_question(topic=topic, difficulty=difficulty)
    print(f"Generated Question: {question}")
    
    # Sample candidate answer (for demonstration)
    answer = "Python uses dynamic typing which means you don't need to declare variable types. It has first-class functions, comprehensions, and a rich standard library. It's widely used for web development, data analysis, and machine learning."
    
    # Evaluate answer
    print("\n=== Evaluate Interview Answer ===")
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    
    evaluation = await evaluate_interview_answer(question=question, answer=answer)
    print("Evaluation:")
    print(f"  Score: {evaluation.get('score', 'N/A')}/10")
    print(f"  Feedback: {evaluation.get('feedback', 'N/A')}")
    print("  Strengths:")
    for strength in evaluation.get('strengths', []):
        print(f"    - {strength}")
    print("  Weaknesses:")
    for weakness in evaluation.get('weaknesses', []):
        print(f"    - {weakness}")
    
    # Generate follow-up question
    print("\n=== Generate Follow-up Question ===")
    follow_up = await generate_follow_up_question(question=question, answer=answer)
    print(f"Follow-up Question: {follow_up}")


async def main():
    """Run all examples."""
    # Check if API key is set
    if not os.environ.get("PERPLEXITY_API_KEY") and not os.environ.get("HUGGINGFACE_API_KEY"):
        print("WARNING: No API key set for any LLM provider. Set PERPLEXITY_API_KEY or HUGGINGFACE_API_KEY environment variable.")
        print("To set a key for this session: export PERPLEXITY_API_KEY='your_api_key_here'")
        return
    
    try:
        await basic_completion_example()
        await chat_completion_example()
        await interview_utility_examples()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 