import requests
import json
import os
import time
import logging # Import the logging module
import asyncio # Add asyncio
import websockets # Add websockets
from typing import Optional, Union # Add Optional and Union
from src.ai.speech import text_to_speech

# Base URL of the Flask API (adjust if your server runs on a different port/host)
BASE_URL = "http://127.0.0.1:5001/api/generate"

# Define available personas and their corresponding voice IDs
PERSONA_VOICES = {
    "professional_uk": "mZ8K1MPRiT5wDQaasg3i", 
    "relatable_indian": "zT03pEAEi0VHKciJODfn",           
    "casual_us_female": "NHRgOEwqx5WZNClv5sat",        
    "conversational_ai": "UgBBYS2sOqTuMpoF3BR0",          
    "clear_uk_female": "rfkTsdZrVWEVhDycUYn9",  
    "calm_ai_therapist": "MpZY6e8MW2zHVi4Vtxrn"       
    # Add more personas and voice IDs as needed
}
DEFAULT_PERSONA = "conversational_ai" # Default if persona is invalid or not provided

# Get a logger instance for this module
logger = logging.getLogger(__name__)

def call_perplexity_api(prompt):
    """Calls the Perplexity generation endpoint."""
    url = f"{BASE_URL}/perplexity"
    payload = {"prompt_text": prompt}
    logger.debug(f"--- Calling Perplexity API ({url}) ---")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        result = response.json()
        logger.debug(f"Response JSON: {json.dumps(result, indent=2)}")
        # Assuming the response JSON has a key like 'response' containing the text
        generated_text = result.get('generated_text')
        if generated_text:
            logger.debug(f"Generated text (first 100 chars): {generated_text[:100]}...")
            return generated_text
        else:
            logger.error("Error: 'generated_text' key not found in Perplexity API JSON response.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Perplexity API: {e}")
        if e.response is not None:
            try:
                logger.error(f"Server response: {e.response.json()}")
            except json.JSONDecodeError:
                logger.error(f"Server response (non-JSON): {e.response.text}")
        return None
    except Exception as e:
        logger.exception(f"An unexpected error occurred during Perplexity API call: {e}")
        return None

def call_huggingface_api(prompt, repo_id=None, max_tokens=None, temp=None):
    """Calls the Hugging Face generation endpoint."""
    url = f"{BASE_URL}/huggingface"
    payload = {"prompt_text": prompt}
    # Add optional parameters if provided
    if repo_id: payload["repo_id"] = repo_id
    if max_tokens: payload["max_new_tokens"] = max_tokens
    if temp is not None: payload["temperature"] = temp
    # Add api_token to payload if you want to pass it explicitly:
    # if HF_API_TOKEN:
    #     payload["api_token"] = HF_API_TOKEN

    logger.debug(f"--- Calling Hugging Face API ({url}) ---")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        result = response.json()
        logger.debug(f"Response JSON: {json.dumps(result, indent=2)}")
        # You might want to extract and return the actual generated text here too
        # generated_text = result.get(...) # Replace ... with the correct key
        # return generated_text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Hugging Face API: {e}")
        if e.response is not None:
            try:
                logger.error(f"Server response: {e.response.json()}")
            except json.JSONDecodeError:
                logger.error(f"Server response (non-JSON): {e.response.text}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during Hugging Face API call: {e}")
        return None # Return None on error

async def generate_and_speak_perplexity(
    prompt: str,
    persona: str = DEFAULT_PERSONA,
    output_filename: str = "perplexity_speech.mp3",
    websocket_url: Optional[str] = None
) -> Union[str, bool, None]:
    """
    Generates text using the Perplexity API, then either generates speech and saves it 
    to a file, or streams the audio to a WebSocket endpoint.

    Args:
        prompt: The text prompt to send to the Perplexity API.
        persona: The persona name to determine the voice. Must be a key in PERSONA_VOICES.
                 Defaults to DEFAULT_PERSONA.
        output_filename: The desired filename for the output audio file (used only if websocket_url is None).
        websocket_url: Optional URL of the WebSocket server to stream audio to. 
                       If provided, audio is streamed; otherwise, it's saved to a file.

    Returns:
        - str: The path to the generated audio file if websocket_url is None and successful.
        - bool: True if WebSocket streaming was successful, False otherwise.
        - None: If Perplexity API call fails or speech generation/streaming fails.
    """
    start_total_time = time.time()
    logger.debug(f"--- Generating and Speaking from Perplexity (Persona: {persona}, Output: {'WebSocket' if websocket_url else output_filename}, Prompt: {prompt[:50]}...) ---")

    # Validate persona and get voice ID
    if persona not in PERSONA_VOICES:
        logger.warning(f"Invalid persona '{persona}'. Falling back to default '{DEFAULT_PERSONA}'.")
        selected_persona = DEFAULT_PERSONA
    else:
        selected_persona = persona
    voice_id = PERSONA_VOICES[selected_persona] # Now retrieves the Voice ID
    logger.debug(f"Using voice ID: {voice_id}")

    # Map persona to voice ID and prepend context
    persona_prompt = f"{selected_persona.replace('_', ' ').capitalize()}: "
    full_prompt = f"{persona_prompt}\n\nUser Prompt: {prompt}"
    logger.debug(f"Full prompt prefix: {full_prompt[:100]}...")

    generated_text = None
    perplexity_duration = 0
    # Time the Perplexity API call
    start_perplexity_time = time.time()
    try:
        generated_text = call_perplexity_api(full_prompt)
        end_perplexity_time = time.time()
        perplexity_duration = end_perplexity_time - start_perplexity_time
        logger.debug(f"Perplexity API call took: {perplexity_duration:.2f} seconds")
    except Exception as e:
        logger.exception(f"Error calling Perplexity API: {e}")
        return None # Exit if Perplexity fails

    if not generated_text:
        logger.warning("Failed to get text from Perplexity API. Cannot generate/stream speech.")
        return None

    # --- Conditional Logic: WebSocket Streaming vs. File Saving --- 
    if websocket_url:
        logger.debug(f"Attempting to stream audio to WebSocket: {websocket_url}")
        start_tts_stream_time = time.time()
        try:
            # Get the audio stream iterator
            audio_iterator = text_to_speech(
                text=generated_text,
                voice=voice_id, 
                stream_audio=True, # Explicitly request streaming
                output_path=None   # Ensure file saving is disabled
            )

            if not audio_iterator:
                logger.error("text_to_speech did not return an audio iterator.")
                return False # Indicate streaming failure

            async with websockets.connect(websocket_url) as websocket:
                logger.info(f"WebSocket connection established to {websocket_url}")
                chunk_count = 0
                async for chunk in audio_iterator: # Elevenlabs iterator is sync, websockets needs async
                    if chunk: # Ensure chunk is not empty
                        await websocket.send(chunk)
                        chunk_count += 1
                        # logger.debug(f"Sent chunk {chunk_count} ({len(chunk)} bytes)")
                logger.info(f"Finished streaming {chunk_count} audio chunks to WebSocket.")
                # Optionally send a completion message if the protocol requires it
                # await websocket.send(json.dumps({"status": "complete"}))
                # Consider adding a short delay before closing if needed
                # await asyncio.sleep(0.1)
                # No explicit close needed with 'async with', but can call websocket.close()
                
            end_tts_stream_time = time.time()
            tts_stream_duration = end_tts_stream_time - start_tts_stream_time
            logger.debug(f"WebSocket streaming took: {tts_stream_duration:.2f} seconds")
            
            end_total_time = time.time()
            total_duration = end_total_time - start_total_time
            logger.debug(f"Total time (WebSocket): {total_duration:.2f} seconds")
            return True # Indicate streaming success

        except websockets.exceptions.InvalidURI:
            logger.error(f"Invalid WebSocket URI: {websocket_url}")
            return False
        except websockets.exceptions.ConnectionClosedOK:
             logger.info("WebSocket connection closed normally by the server.")
             # Decide if this is success or failure based on your protocol
             # For now, assuming it means streaming finished
             end_tts_stream_time = time.time()
             tts_stream_duration = end_tts_stream_time - start_tts_stream_time
             logger.debug(f"WebSocket streaming took: {tts_stream_duration:.2f} seconds (closed OK)")
             end_total_time = time.time()
             total_duration = end_total_time - start_total_time
             logger.debug(f"Total time (WebSocket): {total_duration:.2f} seconds")
             return True # Or potentially False if closure wasn't expected yet
        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(f"WebSocket connection closed with error: {e}")
            return False
        except ConnectionRefusedError:
            logger.error(f"WebSocket connection refused by server at {websocket_url}")
            return False
        except ValueError as ve:
            # Catch specific errors like invalid voice ID from text_to_speech
            logger.error(f"Error during text_to_speech call for streaming: {ve}")
            return False
        except Exception as e:
            # Catch other potential errors (TTS API errors, WebSocket send errors)
            logger.exception(f"An unexpected error occurred during WebSocket streaming: {e}")
            return False

    else:
        # --- Original File Saving Logic --- 
        logger.debug("Generating speech and saving to file...")

        # Define data directory and ensure it exists
        data_dir = "data"
        try:
            os.makedirs(data_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating directory {data_dir}: {e}")
            return None # Cannot proceed if directory creation fails
            
        # Construct full output path
        full_output_path = os.path.join(data_dir, output_filename)

        # Time the Text-to-Speech call for file saving
        start_tts_save_time = time.time()
        try:
            text_to_speech( 
                text=generated_text,
                voice=voice_id, 
                output_path=full_output_path, # Pass the full path here
                stream_audio=False # Ensure streaming is off
            )
            end_tts_save_time = time.time() # Record end time only on success
            tts_save_duration = end_tts_save_time - start_tts_save_time
            logger.debug(f"Audio file generation successful. Output path: {full_output_path}")
            logger.debug(f"Audio file generation took: {tts_save_duration:.2f} seconds")

            end_total_time = time.time()
            total_duration = end_total_time - start_total_time
            logger.debug(f"Total time (File Save): {total_duration:.2f} seconds")
            return full_output_path # Return the file path

        except ValueError as ve:
            logger.error(f"Error calling text_to_speech for file saving: {ve}")
            return None
        except TypeError as te:
            logger.error(f"Type error calling text_to_speech: {te}")
            logger.error("Please ensure the text_to_speech function signature is correct.")
            return None
        except Exception as e:
            end_tts_save_time = time.time() # Record time even on failure
            tts_save_duration = end_tts_save_time - start_tts_save_time
            logger.exception(f"Error during text-to-speech conversion for file saving: {e}")
            logger.debug(f"Text-to-speech file saving attempt took: {tts_save_duration:.2f} seconds before failing.")
            return None

async def main(): # Create an async main function
    # Make sure the Flask server (src/app.py) is running before executing this script.
    DEBUG_MODE = True  # Set to True to see detailed output, False to hide it

    # --- Configure Logging --- 
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # --- End Logging Configuration --- 

    # 1. Test the updated generate_and_speak_perplexity (File Saving)
    # print("\n--- Testing Perplexity Generate and Speak (File Saving - Relatable Indian Persona) ---")
    # default_prompt = "What is polymorphism in object-oriented programming? Output one paragraph only, with 100 words."
    # audio_file_path_default = await generate_and_speak_perplexity(
    #     prompt=default_prompt,
    #     persona="relatable_indian", 
    #     output_filename="polymorphism_relatable_indian.mp3",
    #     websocket_url=None # Explicitly None for file saving
    # )
    # if audio_file_path_default:
    #     print(f"Audio generated and saved to: {audio_file_path_default}")
    # else:
    #     print("Generate and speak function failed (File Saving - Relatable Indian Persona).")

    # 2. Test the updated generate_and_speak_perplexity (WebSocket Streaming)
    print("\n--- Testing Perplexity Generate and Speak (WebSocket Streaming - Clear UK Female Persona) ---")
    websocket_prompt = "Explain the concept of asynchronous programming in Python using asyncio."
    # Replace with your actual running WebSocket server URL
    test_websocket_url = "ws://localhost:8765" # EXAMPLE URL - CHANGE THIS!
    
    print(f"Attempting to stream to: {test_websocket_url}")
    print("Please ensure a WebSocket server is running at this address and listening for binary audio data.")
    
    streaming_success = await generate_and_speak_perplexity(
        prompt=websocket_prompt,
        persona="clear_uk_female", # Use a different persona/voice
        websocket_url=test_websocket_url # Provide the URL to trigger streaming
        # output_filename is ignored when websocket_url is provided
    )

    if streaming_success:
        print(f"WebSocket streaming initiated successfully to {test_websocket_url}.")
    else:
        print(f"WebSocket streaming failed to {test_websocket_url}.")

    # Example calling Hugging Face (remains unchanged)
    # print("\n--- Testing HuggingFace API Call with Custom Params ---")
    # call_huggingface_api(
    #     prompt="Tell me a short story about a robot learning to paint.",
    #     repo_id="google/gemma-7b-it", 
    #     max_tokens=100,
    #     temp=0.8,
    # )

if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")