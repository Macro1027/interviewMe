"""
Voice Synthesis Module for the AI Interview Simulation Platform.

This module provides text-to-speech capabilities using the Google Cloud Text-to-Speech API.
"""
from src.ai.voice_synthesis.service import (
    VoiceSynthesisService,
    get_voice_synthesis_service,
    synthesize_interviewer_response,
    add_thinking_sounds
)

__all__ = [
    'VoiceSynthesisService',
    'get_voice_synthesis_service',
    'synthesize_interviewer_response',
    'add_thinking_sounds'
]
