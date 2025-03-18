"""
Voice synthesis service for the AI Interview Simulation Platform.

This module provides text-to-speech capabilities using the Google Cloud Text-to-Speech API.
It includes functionality for different voice profiles, persona-based configuration,
response caching, and natural speech patterns.
"""
import os
import json
import random
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import aiofiles
import aiofiles.os

# Import Google Cloud libraries
from google.cloud import texttospeech
from google.oauth2 import service_account


class VoiceSynthesisService:
    """
    Service for text-to-speech synthesis using Google Cloud Text-to-Speech API.
    
    This service provides methods to convert text to speech with various voice options,
    including language, gender, speaking rate, and pitch. It also implements caching
    to improve performance and reduce API costs.
    
    Attributes:
        default_language_code (str): The default language code for synthesis.
        default_voice_name (str): The default voice name for synthesis.
        cache_dir (str): Directory for caching generated audio files.
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        cache_dir: Optional[str] = None,
        default_language_code: str = "en-US",
        default_voice_name: str = "en-US-Neural2-F"
    ):
        """
        Initialize the voice synthesis service.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON file.
                If None, uses the GOOGLE_APPLICATION_CREDENTIALS environment variable.
            cache_dir: Directory for caching generated audio files.
                If None, uses a default directory in the user's home.
            default_language_code: Default language code for synthesis.
            default_voice_name: Default voice name for synthesis.
        """
        self.default_language_code = default_language_code
        self.default_voice_name = default_voice_name
        
        # Set up cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".interviewme", "tts_cache")
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize Google Cloud client
        self._client = self._initialize_client(credentials_path)
    
    def _initialize_client(self, credentials_path: Optional[str]) -> texttospeech.TextToSpeechClient:
        """
        Initialize the Google Cloud Text-to-Speech client.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON file.
                If None, uses the GOOGLE_APPLICATION_CREDENTIALS environment variable.
        
        Returns:
            A configured TextToSpeechClient instance.
        """
        if credentials_path:
            # Use explicit credentials
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            return texttospeech.TextToSpeechClient(credentials=credentials)
        else:
            # Use default credentials from GOOGLE_APPLICATION_CREDENTIALS env var
            return texttospeech.TextToSpeechClient()
    
    def _get_cache_filename(
        self,
        text: str,
        voice_name: str,
        speaking_rate: float,
        pitch: float,
        gender: str,
        language_code: str,
        volume_gain_db: float
    ) -> str:
        """
        Generate a cache filename based on the text and voice parameters.
        
        Args:
            text: The text to synthesize.
            voice_name: The voice name to use.
            speaking_rate: The speaking rate.
            pitch: The pitch adjustment.
            gender: The voice gender.
            language_code: The language code.
            volume_gain_db: The volume gain in dB.
        
        Returns:
            A unique filename for the cached audio file.
        """
        # Create a string representation of the parameters
        params_str = f"{text}:{voice_name}:{speaking_rate}:{pitch}:{gender}:{language_code}:{volume_gain_db}"
        
        # Generate a hash of the parameters
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        # Create a filename with the hash
        return os.path.join(self.cache_dir, f"tts_{params_hash}.mp3")
    
    async def synthesize_text(
        self,
        text: str,
        language_code: Optional[str] = None,
        voice_name: Optional[str] = None,
        gender: str = "FEMALE",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        use_cache: bool = True
    ) -> bytes:
        """
        Synthesize text to speech.
        
        Args:
            text: The text to synthesize.
            language_code: The language code (e.g., "en-US").
            voice_name: The voice name (e.g., "en-US-Neural2-F").
            gender: The voice gender ("MALE", "FEMALE", or "NEUTRAL").
            speaking_rate: Speech speed (0.25 to 4.0).
            pitch: Voice pitch (-20.0 to 20.0).
            volume_gain_db: Volume adjustment (-96.0 to 16.0).
            use_cache: Whether to use the cache.
        
        Returns:
            The audio content as bytes.
        """
        # Use defaults if parameters are not provided
        language_code = language_code or self.default_language_code
        voice_name = voice_name or self.default_voice_name
        
        # Generate cache filename
        cache_filename = self._get_cache_filename(
            text=text,
            voice_name=voice_name,
            speaking_rate=speaking_rate,
            pitch=pitch,
            gender=gender,
            language_code=language_code,
            volume_gain_db=volume_gain_db
        )
        
        # Check cache if enabled
        if use_cache and os.path.exists(cache_filename):
            try:
                # Check if the file exists and has content
                stat_result = await aiofiles.os.stat(cache_filename)
                if stat_result.st_size > 0:
                    # Read cached audio
                    async with aiofiles.open(cache_filename, 'rb') as f:
                        return await f.read()
            except Exception as e:
                print(f"Error reading cache file: {e}")
        
        # Synthesize speech (run in thread pool to avoid blocking)
        audio_content = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._synthesize_text_sync(
                text=text,
                language_code=language_code,
                voice_name=voice_name,
                gender=gender,
                speaking_rate=speaking_rate,
                pitch=pitch,
                volume_gain_db=volume_gain_db
            )
        )
        
        # Save to cache if enabled
        if use_cache:
            try:
                async with aiofiles.open(cache_filename, 'wb') as f:
                    await f.write(audio_content)
            except Exception as e:
                print(f"Error writing cache file: {e}")
        
        return audio_content
    
    def _synthesize_text_sync(
        self,
        text: str,
        language_code: str,
        voice_name: str,
        gender: str,
        speaking_rate: float,
        pitch: float,
        volume_gain_db: float
    ) -> bytes:
        """
        Synchronous implementation of text-to-speech synthesis.
        
        Args:
            text: The text to synthesize.
            language_code: The language code.
            voice_name: The voice name.
            gender: The voice gender.
            speaking_rate: The speaking rate.
            pitch: The pitch adjustment.
            volume_gain_db: The volume gain in dB.
        
        Returns:
            The audio content as bytes.
        """
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=getattr(texttospeech.SsmlVoiceGender, gender)
        )
        
        # Select the type of audio file to return
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db
        )
        
        # Perform the text-to-speech request
        response = self._client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return the audio content
        return response.audio_content
    
    async def save_audio_file(self, audio_content: bytes, file_path: str) -> None:
        """
        Save audio content to a file.
        
        Args:
            audio_content: The audio content as bytes.
            file_path: The path to save the audio file.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write the audio content to the file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(audio_content)
    
    async def list_available_voices(self, language_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available voices from Google Cloud Text-to-Speech API.
        
        Args:
            language_code: Filter voices by language code prefix.
                If None, returns all available voices.
        
        Returns:
            A list of voice information dictionaries.
        """
        # Get voices (run in thread pool to avoid blocking)
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._client.list_voices(language_code=language_code)
        )
        
        # Convert to simplified dictionaries
        voices = []
        for voice in response.voices:
            voice_dict = {
                "name": voice.name,
                "gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                "language_codes": list(voice.language_codes),
                "natural_sample_rate_hertz": voice.natural_sample_rate_hertz
            }
            voices.append(voice_dict)
        
        return voices


# Singleton instance cache
_voice_synthesis_service = None


async def get_voice_synthesis_service() -> VoiceSynthesisService:
    """
    Get or create the voice synthesis service singleton.
    
    Returns:
        A configured VoiceSynthesisService instance.
    """
    global _voice_synthesis_service
    
    if _voice_synthesis_service is None:
        # Get credentials path from environment variable
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Create service
        _voice_synthesis_service = VoiceSynthesisService(
            credentials_path=credentials_path
        )
    
    return _voice_synthesis_service


# Higher-level utility functions

async def add_thinking_sounds(text: str) -> str:
    """
    Add thinking sounds to make speech sound more natural.
    
    Args:
        text: The original text.
    
    Returns:
        Text with thinking sounds added.
    """
    # Define thinking sounds
    thinking_sounds = [
        "Hmm...",
        "Let's see...",
        "Well...",
        "Um...",
        "So...",
        "Okay...",
        "Alright..."
    ]
    
    # Randomly decide whether to add a thinking sound (70% chance)
    if random.random() < 0.7:
        thinking_sound = random.choice(thinking_sounds)
        # Add the thinking sound at the beginning
        text = f"{thinking_sound} {text}"
    
    return text


async def synthesize_interviewer_response(
    text: str,
    persona: str = "professional",
    add_natural_sounds: bool = True
) -> bytes:
    """
    Synthesize an interviewer response with a specific persona.
    
    Args:
        text: The text to synthesize.
        persona: The interviewer persona ("professional", "friendly", or "technical").
        add_natural_sounds: Whether to add thinking sounds for natural speech.
    
    Returns:
        The audio content as bytes.
    """
    # Get the voice synthesis service
    service = await get_voice_synthesis_service()
    
    # Add thinking sounds if requested
    if add_natural_sounds:
        text = await add_thinking_sounds(text)
    
    # Configure voice based on persona
    if persona == "professional":
        # Professional persona - clear, measured speech
        return await service.synthesize_text(
            text=text,
            voice_name="en-US-Neural2-F",
            gender="FEMALE",
            speaking_rate=0.95,
            pitch=0.0
        )
    elif persona == "friendly":
        # Friendly persona - slightly faster, more animated
        return await service.synthesize_text(
            text=text,
            voice_name="en-US-Neural2-F",
            gender="FEMALE",
            speaking_rate=1.05,
            pitch=1.5
        )
    elif persona == "technical":
        # Technical persona - male voice, deliberate pace
        return await service.synthesize_text(
            text=text,
            voice_name="en-US-Neural2-D",
            gender="MALE",
            speaking_rate=0.9,
            pitch=-1.0
        )
    else:
        # Default to professional
        return await service.synthesize_text(
            text=text,
            voice_name="en-US-Neural2-F",
            gender="FEMALE",
            speaking_rate=0.95,
            pitch=0.0
        ) 