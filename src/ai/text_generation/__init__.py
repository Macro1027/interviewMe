"""
Text Generation Module for AI Interview Simulation Platform.

This module provides a unified interface for text generation using various
language model providers such as Perplexity and Hugging Face.
"""

from .text_generation import (
    TextGenerationService,
    generate_interview_question,
    evaluate_answer,
    generate_followup_question
)

__all__ = [
    'TextGenerationService',
    'generate_interview_question',
    'evaluate_answer',
    'generate_followup_question'
] 