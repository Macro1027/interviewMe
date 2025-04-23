import os
from elevenlabs import play, save, stream
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from typing import Iterator, Union, Optional

# Load environment variables from .env file
load_dotenv()

# Initialize ElevenLabs client
# Make sure your ELEVENLABS_API_KEY is set in your .env file
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
print(f"ELEVENLABS_API_KEY loaded: {bool(ELEVENLABS_API_KEY)}") # Add this line for debugging

if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY not found in environment variables.")
    # You might want to raise an error or handle this case more robustly
    client = None 
else:
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech(text: str, voice: str = "Rachel", model: str = "eleven_flash_v2_5", output_path: Optional[str] = None, stream_audio: bool = False) -> Union[bytes, None, Iterator[bytes]]:
    """
    Converts text to speech using ElevenLabs API.

    The function can:
    1. Save the audio to a file if output_path is provided.
    2. Return an audio stream iterator if stream_audio is True and output_path is None.
    3. Play the audio after generation if both output_path and stream_audio are None/False.

    Args:
        text (str): The text to convert to speech.
        voice (str): The name or ID of the voice to use (default: "Rachel").
                     Find voices using client.voices.get_all().voices or the ElevenLabs website.
                     Note: Streaming requires a voice ID.
        model (str): The model to use (default: "eleven_flash_v2_5").
        output_path (str, optional): If provided, saves the audio to this file path (e.g., 'output.mp3'). 
                                     Takes precedence over streaming. Defaults to None.
        stream_audio (bool, optional): If True and output_path is None, returns an iterator yielding audio chunks.
                                       Requires 'voice' to be a valid voice ID. Defaults to False.

    Returns:
        Union[bytes, None, Iterator[bytes]]: 
            - bytes: The audio data as bytes if played directly (output_path=None, stream_audio=False).
            - None: If the audio is saved to a file (output_path is provided).
            - Iterator[bytes]: An iterator yielding audio chunks if streamed (stream_audio=True, output_path=None).

    Raises:
        ValueError: If the ElevenLabs client failed to initialize (e.g., missing API key).
        ValueError: If streaming is requested but the provided 'voice' doesn't seem to be a valid ID (heuristic check). 
                    The API call itself might also fail if the ID is invalid.
        Exception: For other API-related errors during generation or streaming.
    """
    if not client:
        raise ValueError("ElevenLabs client not initialized. Check API key.")

    try:
        print(f'Processing text: "{text[:50]}..."') 
        
        if output_path:
            print(f'Generating speech and saving to {output_path}...')
            audio = client.generate(text=text, voice=voice, model=model)
            save(audio, output_path)
            print(f"Audio saved to {output_path}")
            return None # Indicate saving, return no bytes
            
        elif stream_audio:
            # Basic check: Voice IDs are typically longer strings of letters/numbers
            # This is a heuristic and might not be perfectly accurate.
            # The API call `convert_as_stream` expects `voice_id`.
            # if not isinstance(voice, str) or len(voice) < 10: # Example heuristic check
            #     raise ValueError(f"Streaming requires a valid voice ID, received: '{voice}'")
            
            print("Generating audio stream iterator...")
            # Note: client.text_to_speech.convert_as_stream expects model_id and voice_id
            audio_stream = client.text_to_speech.convert_as_stream(
                text=text,
                voice_id=voice, # Pass the voice parameter here, assuming it's an ID for streaming
                model_id=model  # Parameter name is model_id here
            )
            # stream(audio_stream) # Don't play the stream here
            # print("Streaming finished.") # Remove this line
            # return None # Indicate streaming, return no bytes
            return audio_stream # Return the iterator itself
            
        else:
            print("Generating and playing audio directly...")
            audio = client.generate(text=text, voice=voice, model=model)
            print("Playing audio...")
            play(audio)
            return audio # Return audio bytes for direct playback/use

    except Exception as e:
        print(f"Error during speech processing: {e}")
        # Implement fallback mechanism here if needed
        raise # Re-raise the exception for the caller to handle

if __name__ == "__main__":
    example_text = "Hello! This is a test of the ElevenLabs text-to-speech API streaming feature."
    # Find a valid voice ID from your ElevenLabs account or use client.voices.get_all()
    # Example voice ID for "Rachel" is "21m00Tcm4TlvDq8ikWAM" (check if still valid)
    example_voice_id = "21m00Tcm4TlvDq8ikWAM" # Replace with a known valid ID if needed

    try:
        # 1. Save to file
        print("\n--- Testing saving to file ---")
        text_to_speech(example_text, voice=example_voice_id, output_path="hello_test_save.mp3")

        # 2. Play directly (default) - Keep commented out
        # print("\n--- Testing direct playback ---")
        # audio_bytes = text_to_speech(example_text, voice=example_voice_id)
        # if audio_bytes:
        #     print(f"Direct playback returned {len(audio_bytes)} bytes.")

        # 3. Get stream iterator
        print("\n--- Testing getting stream iterator ---")
        # Use a known voice ID for streaming
        audio_iterator = text_to_speech(example_text, voice=example_voice_id, stream_audio=True)
        if audio_iterator:
            print(f"Successfully obtained audio stream iterator: {audio_iterator}")
            # We won't consume it here in the main block as it requires an async context usually
            # for chunk in audio_iterator:
            #     print(f"Received chunk of size: {len(chunk)}")
        else:
             print("Failed to obtain audio stream iterator.")

    except ValueError as ve:
        print(f"Configuration or Initialization error: {ve}")
    except Exception as e:
        print(f"API error: {e}")