"""
Text Generation Module for the AI Interview Simulation Platform.

This module provides text generation capabilities using various LLM providers.
"""
from src.ai.text_generation.text_generation import (
    TextGenerationService,
    get_text_generation_service,
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)

__all__ = [
    'TextGenerationService',
    'get_text_generation_service',
    'generate_interview_question',
    'evaluate_interview_answer',
    'generate_follow_up_question'
] 