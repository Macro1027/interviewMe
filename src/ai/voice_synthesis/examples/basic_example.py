#!/usr/bin/env python
"""
Example script demonstrating how to use the voice synthesis service.

This script shows how to generate speech, save it to a file, and work with different voice profiles.

Usage:
    python -m src.ai.voice_synthesis.examples.basic_example

Make sure to set the GOOGLE_APPLICATION_CREDENTIALS environment variable before running.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from src.ai.voice_synthesis.service import (
    get_voice_synthesis_service,
    synthesize_interviewer_response,
    add_thinking_sounds
)
from src.utils.logger import setup_logger

# Set up logger
logger = setup_logger("voice_synthesis_example")


async def test_basic_synthesis():
    """Test basic text-to-speech synthesis."""
    logger.info("Testing basic text-to-speech synthesis...")
    
    # Get the voice synthesis service
    service = await get_voice_synthesis_service()
    
    # Generate speech
    text = "Hello! I'm the AI interviewer assistant. I'll be asking you some questions today."
    audio_content = await service.synthesize_text(
        text=text,
        speaking_rate=1.0,
        pitch=0.0
    )
    
    # Save to file
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "basic_synthesis.mp3")
    
    await service.save_audio_file(audio_content, file_path)
    logger.info(f"Basic synthesis saved to: {file_path}")
    
    return file_path


async def test_different_voices():
    """Test different voice profiles."""
    logger.info("Testing different voice profiles...")
    
    service = await get_voice_synthesis_service()
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    
    # Text to synthesize
    text = "Could you tell me about a time when you had to work under pressure to meet a deadline?"
    
    # Test different voices
    voices = [
        {"name": "female", "voice_name": "en-US-Neural2-F", "gender": "FEMALE"},
        {"name": "male", "voice_name": "en-US-Neural2-D", "gender": "MALE"},
        {"name": "slow", "voice_name": "en-US-Neural2-F", "speaking_rate": 0.8},
        {"name": "fast", "voice_name": "en-US-Neural2-F", "speaking_rate": 1.2},
        {"name": "high_pitch", "voice_name": "en-US-Neural2-F", "pitch": 5.0},
        {"name": "low_pitch", "voice_name": "en-US-Neural2-F", "pitch": -5.0},
    ]
    
    for voice in voices:
        name = voice.pop("name")
        
        # Generate speech with this voice profile
        audio_content = await service.synthesize_text(
            text=text,
            **voice
        )
        
        # Save to file
        file_path = os.path.join(output_dir, f"voice_{name}.mp3")
        await service.save_audio_file(audio_content, file_path)
        results[name] = file_path
        logger.info(f"Voice profile '{name}' saved to: {file_path}")
    
    return results


async def test_interview_personas():
    """Test different interviewer personas."""
    logger.info("Testing different interviewer personas...")
    
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    
    # Test different personas
    personas = ["professional", "friendly", "technical"]
    
    for persona in personas:
        # Sample interview question for this persona
        if persona == "professional":
            text = "Tell me about your experience working in cross-functional teams."
        elif persona == "friendly":
            text = "What's something you're really passionate about outside of work?"
        else:  # technical
            text = "Could you walk me through how you would implement a cache with an LRU eviction policy?"
        
        # Generate speech for this persona
        audio_content = await synthesize_interviewer_response(text, persona)
        
        # Save to file
        file_path = os.path.join(output_dir, f"persona_{persona}.mp3")
        service = await get_voice_synthesis_service()
        await service.save_audio_file(audio_content, file_path)
        results[persona] = file_path
        logger.info(f"Persona '{persona}' saved to: {file_path}")
    
    return results


async def test_natural_speech():
    """Test natural speech with thinking sounds."""
    logger.info("Testing natural speech with thinking sounds...")
    
    service = await get_voice_synthesis_service()
    
    # Original text
    original_text = "Let's discuss your approach to problem-solving. Can you describe a challenging problem you faced in your previous role? How did you identify the root cause? What steps did you take to resolve it? Were there any lessons learned from that experience?"
    
    # Add thinking sounds
    modified_text = await add_thinking_sounds(original_text)
    
    # Synthesize both versions
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Original version
    original_audio = await service.synthesize_text(
        text=original_text,
        speaking_rate=0.95
    )
    original_path = os.path.join(output_dir, "speech_original.mp3")
    await service.save_audio_file(original_audio, original_path)
    
    # Natural version
    natural_audio = await service.synthesize_text(
        text=modified_text,
        speaking_rate=0.95
    )
    natural_path = os.path.join(output_dir, "speech_natural.mp3")
    await service.save_audio_file(natural_audio, natural_path)
    
    logger.info(f"Original speech saved to: {original_path}")
    logger.info(f"Natural speech saved to: {natural_path}")
    
    return {
        "original": original_path,
        "natural": natural_path,
        "original_text": original_text,
        "modified_text": modified_text
    }


async def list_available_voices():
    """List available voices from Google TTS."""
    logger.info("Listing available voices...")
    
    service = await get_voice_synthesis_service()
    
    # Get all English voices
    voices = await service.list_available_voices(language_code="en-")
    
    logger.info(f"Found {len(voices)} English voices")
    
    # Print details of the first 5 voices
    for i, voice in enumerate(voices[:5]):
        logger.info(f"Voice {i+1}:")
        logger.info(f"  Name: {voice['name']}")
        logger.info(f"  Gender: {voice['gender']}")
        logger.info(f"  Language Codes: {', '.join(voice['language_codes'])}")
    
    return voices


async def main():
    """Run all examples."""
    try:
        # Check if Google credentials are set
        if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
            logger.error("Please set this variable to the path of your Google Cloud credentials JSON file.")
            return
        
        # List available voices
        await list_available_voices()
        print("\n" + "-" * 50 + "\n")
        
        # Run the basic example
        await test_basic_synthesis()
        print("\n" + "-" * 50 + "\n")
        
        # Test different voices
        await test_different_voices()
        print("\n" + "-" * 50 + "\n")
        
        # Test different personas
        await test_interview_personas()
        print("\n" + "-" * 50 + "\n")
        
        # Test natural speech
        result = await test_natural_speech()
        logger.info("Original text:")
        logger.info(result["original_text"])
        logger.info("\nModified text with thinking sounds:")
        logger.info(result["modified_text"])
        
    except Exception as e:
        logger.error(f"Error running example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 