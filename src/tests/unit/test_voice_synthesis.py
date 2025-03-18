"""
Unit tests for the voice synthesis service.

This file contains tests for the voice synthesis service, focusing on core functionality
and mocking external API calls to the Google Cloud Text-to-Speech API.
"""
import os
import json
import pytest
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.ai.voice_synthesis.service import (
    VoiceSynthesisService,
    get_voice_synthesis_service,
    synthesize_interviewer_response,
    add_thinking_sounds
)


@pytest.fixture
def mock_texttospeech_client():
    """Mock the Google Cloud Text-to-Speech client."""
    with patch('google.cloud.texttospeech.TextToSpeechClient') as mock_client:
        # Mock synthesize_speech method
        mock_resp = MagicMock()
        mock_resp.audio_content = b'mocked_audio_content'
        mock_client.return_value.synthesize_speech.return_value = mock_resp
        
        # Mock list_voices method
        mock_voice = MagicMock()
        mock_voice.name = "en-US-Neural2-F"
        mock_voice.ssml_gender = "FEMALE"
        mock_voice.language_codes = ["en-US"]
        mock_voice2 = MagicMock()
        mock_voice2.name = "en-US-Neural2-D"
        mock_voice2.ssml_gender = "MALE"
        mock_voice2.language_codes = ["en-US"]
        
        mock_voices_resp = MagicMock()
        mock_voices_resp.voices = [mock_voice, mock_voice2]
        mock_client.return_value.list_voices.return_value = mock_voices_resp
        
        yield mock_client


@pytest.fixture
def mock_aiofiles():
    """Mock aiofiles for async file operations."""
    with patch('aiofiles.open', new_callable=AsyncMock) as mock_open:
        mock_file = AsyncMock()
        mock_open.return_value.__aenter__.return_value = mock_file
        yield mock_open


@pytest.fixture
def voice_service(mock_texttospeech_client, tmp_path):
    """Create a VoiceSynthesisService instance with mocked dependencies."""
    service = VoiceSynthesisService(
        credentials_path=None,  # Use default credentials
        cache_dir=str(tmp_path),
        default_language_code="en-US",
        default_voice_name="en-US-Neural2-F"
    )
    service._client = mock_texttospeech_client.return_value
    return service


class TestVoiceSynthesisService:
    """Tests for the VoiceSynthesisService class."""
    
    def test_init(self, voice_service):
        """Test initialization of the service."""
        assert voice_service.default_language_code == "en-US"
        assert voice_service.default_voice_name == "en-US-Neural2-F"
        assert voice_service._client is not None
    
    async def test_synthesize_text(self, voice_service, mock_texttospeech_client):
        """Test synthesizing text to speech."""
        # Call the method
        result = await voice_service.synthesize_text(
            text="Hello, this is a test.",
            language_code="en-US",
            voice_name="en-US-Neural2-F",
            speaking_rate=1.0,
            pitch=0.0
        )
        
        # Verify result
        assert result == b'mocked_audio_content'
        
        # Verify the client was called with correct parameters
        call_args = mock_texttospeech_client.return_value.synthesize_speech.call_args[0]
        input_text = call_args[0]
        voice = call_args[1]
        audio_config = call_args[2]
        
        assert input_text.text == "Hello, this is a test."
        assert voice.language_code == "en-US"
        assert voice.name == "en-US-Neural2-F"
        assert voice.ssml_gender == "FEMALE"
        assert audio_config.speaking_rate == 1.0
        assert audio_config.pitch == 0.0
    
    async def test_synthesize_text_with_cache(self, voice_service, mock_texttospeech_client, mock_aiofiles, tmp_path):
        """Test caching mechanism in text synthesis."""
        # Mock os.path.exists to control cache hits/misses
        with patch('os.path.exists') as mock_exists:
            # First call - cache miss
            mock_exists.return_value = False
            await voice_service.synthesize_text(
                text="Hello, this is a test.",
                use_cache=True
            )
            
            # Verify synthesis was called
            assert mock_texttospeech_client.return_value.synthesize_speech.call_count == 1
            
            # Second call - cache hit
            mock_exists.return_value = True
            with patch('aiofiles.os.stat') as mock_stat:
                mock_stat_result = MagicMock()
                mock_stat_result.st_size = 100  # non-zero file size
                mock_stat.return_value = mock_stat_result
                
                # Mock file read
                mock_aiofiles.return_value.__aenter__.return_value.read = AsyncMock(
                    return_value=b'cached_audio_content'
                )
                
                result = await voice_service.synthesize_text(
                    text="Hello, this is a test.",
                    use_cache=True
                )
            
            # Verify result comes from cache
            assert result == b'cached_audio_content'
            
            # Verify synthesis was not called again
            assert mock_texttospeech_client.return_value.synthesize_speech.call_count == 1
    
    async def test_list_available_voices(self, voice_service):
        """Test listing available voices."""
        voices = await voice_service.list_available_voices()
        
        # Verify we got the expected voices
        assert len(voices) == 2
        assert voices[0]["name"] == "en-US-Neural2-F"
        assert voices[0]["gender"] == "FEMALE"
        assert voices[0]["language_codes"] == ["en-US"]
        
        assert voices[1]["name"] == "en-US-Neural2-D"
        assert voices[1]["gender"] == "MALE"
        assert voices[1]["language_codes"] == ["en-US"]
    
    async def test_save_audio_file(self, voice_service, mock_aiofiles):
        """Test saving audio content to a file."""
        audio_content = b'test_audio_content'
        file_path = "/tmp/test_audio.mp3"
        
        await voice_service.save_audio_file(audio_content, file_path)
        
        # Verify file was opened and written to
        mock_aiofiles.assert_called_once_with(file_path, 'wb')
        mock_aiofiles.return_value.__aenter__.return_value.write.assert_called_once_with(audio_content)
    
    def test_get_cache_filename(self, voice_service):
        """Test generation of cache filenames."""
        text = "Hello, this is a test."
        voice_name = "en-US-Neural2-F"
        
        # Calculate expected hash
        params_str = f"{text}:{voice_name}:1.0:0.0:FEMALE:en-US:0.0"
        expected_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        # Get cache filename
        filename = voice_service._get_cache_filename(
            text=text,
            voice_name=voice_name,
            speaking_rate=1.0,
            pitch=0.0,
            gender="FEMALE",
            language_code="en-US",
            volume_gain_db=0.0
        )
        
        # Verify filename
        assert expected_hash in filename
        assert filename.endswith(".mp3")


class TestHighLevelFunctions:
    """Tests for the high-level voice synthesis functions."""
    
    @pytest.fixture
    def mock_get_service(self):
        """Mock the get_voice_synthesis_service function."""
        with patch('src.ai.voice_synthesis.service.get_voice_synthesis_service') as mock:
            mock_service = AsyncMock()
            mock_service.synthesize_text = AsyncMock(return_value=b'mocked_audio')
            mock.return_value = mock_service
            yield mock
    
    async def test_add_thinking_sounds(self):
        """Test adding thinking sounds to text."""
        original_text = "Tell me about your experience."
        
        # Patch the random choice to return a predictable value
        with patch('random.choice', return_value="Hmm..."):
            modified_text = await add_thinking_sounds(original_text)
        
        # Verify thinking sound was added
        assert modified_text.startswith("Hmm...")
        assert original_text in modified_text
    
    async def test_synthesize_interviewer_response(self, mock_get_service):
        """Test synthesizing an interviewer response with a specific persona."""
        # Call the function with different personas
        personas = ["professional", "friendly", "technical"]
        
        for persona in personas:
            await synthesize_interviewer_response(
                "Test question?",
                persona=persona
            )
            
            # Verify the service was called with appropriate parameters for this persona
            service = await mock_get_service.return_value
            
            # The last call should match our persona
            call_args = service.synthesize_text.call_args.kwargs
            
            # Verify basic params
            assert "Test question?" in call_args.get("text", "")
            
            # Different personas should have different voice characteristics
            if persona == "professional":
                assert call_args.get("speaking_rate", None) is not None
            elif persona == "friendly":
                assert call_args.get("speaking_rate", None) is not None  
            elif persona == "technical":
                assert call_args.get("speaking_rate", None) is not None 