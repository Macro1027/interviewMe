# Voice Synthesis Module

This module provides text-to-speech capabilities for the AI Interview Simulation Platform using the Google Cloud Text-to-Speech API.

## Features

- High-quality neural text-to-speech synthesis
- Support for different voice profiles (gender, language, accent)
- Persona-based voice configuration (professional, friendly, technical)
- Response caching to improve performance and reduce API costs
- Natural speech patterns with thinking sounds and pauses
- Asynchronous API for non-blocking operation

## Setup

### Prerequisites

To use this module, you need:

1. A Google Cloud account
2. A project with the Text-to-Speech API enabled
3. A service account key (JSON file)

### Installation

1. Install the required dependencies:
   ```bash
   pip install google-cloud-texttospeech aiofiles
   ```

2. Set up your Google Cloud credentials:
   ```bash
   python -m src.ai.voice_synthesis.examples.set_google_credentials
   ```

3. Make sure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set to the path of your service account key file.

## Usage

### Basic Usage

```python
import asyncio
from src.ai.voice_synthesis.service import get_voice_synthesis_service

async def main():
    # Get the voice synthesis service
    service = await get_voice_synthesis_service()
    
    # Synthesize text to speech
    audio_content = await service.synthesize_text(
        text="Hello, I'm your AI interviewer today. How are you doing?",
        language_code="en-US",
        voice_name="en-US-Neural2-F",
        speaking_rate=1.0,
        pitch=0.0
    )
    
    # Save to file
    await service.save_audio_file(audio_content, "output/greeting.mp3")

if __name__ == "__main__":
    asyncio.run(main())
```

### Interviewer Personas

The module provides predefined interviewer personas:

```python
from src.ai.voice_synthesis.service import synthesize_interviewer_response

async def generate_persona_speech():
    # Professional persona
    prof_audio = await synthesize_interviewer_response(
        "Tell me about your experience with team leadership.",
        persona="professional"
    )
    
    # Friendly persona
    friendly_audio = await synthesize_interviewer_response(
        "What do you enjoy doing outside of work?",
        persona="friendly"
    )
    
    # Technical persona
    tech_audio = await synthesize_interviewer_response(
        "Could you explain your approach to unit testing?",
        persona="technical"
    )
```

### Natural Speech Patterns

The module can add thinking sounds and pauses to make speech sound more natural:

```python
from src.ai.voice_synthesis.service import add_thinking_sounds

async def natural_speech_example():
    # Original text
    original = "Tell me about a challenging project you worked on."
    
    # Add thinking sounds and pauses
    natural = await add_thinking_sounds(original)
    
    print(f"Original: {original}")
    print(f"Natural: {natural}")
    # Output:
    # Original: Tell me about a challenging project you worked on.
    # Natural: Hmm... Tell me about a challenging project you worked on.
```

## Voice Configuration

### Available Voice Parameters

- `language_code`: The language code (e.g., "en-US", "en-GB", "fr-FR")
- `voice_name`: The specific voice name (e.g., "en-US-Neural2-F")
- `gender`: The voice gender ("MALE", "FEMALE", "NEUTRAL")
- `speaking_rate`: Speech speed (0.25 to 4.0, default: 1.0)
- `pitch`: Voice pitch (-20.0 to 20.0, default: 0.0)
- `volume_gain_db`: Volume adjustment (-96.0 to 16.0, default: 0.0)

### Listing Available Voices

```python
async def list_voices():
    service = await get_voice_synthesis_service()
    
    # Get all English voices
    english_voices = await service.list_available_voices(language_code="en-")
    
    # Get all voices for a specific language
    french_voices = await service.list_available_voices(language_code="fr-FR")
    
    # Print voice details
    for voice in english_voices[:5]:
        print(f"Name: {voice['name']}")
        print(f"Gender: {voice['gender']}")
        print(f"Language Codes: {', '.join(voice['language_codes'])}")
```

## Performance Considerations

- The service implements caching to improve performance and reduce API costs
- Audio files are saved with a hash of the text and voice parameters
- Cached files are reused when the same text and parameters are requested
- Cache can be bypassed with `use_cache=False` when needed

## Examples

See the `examples` directory for more usage examples:

- `basic_example.py`: Demonstrates basic usage and voice configurations
- `set_google_credentials.py`: Helps set up Google Cloud credentials

## Integration with Interview Flow

The voice synthesis service is integrated with the interview flow through the interview service:

```python
from src.app.services.interview_service import InterviewService
from src.ai.voice_synthesis.service import synthesize_interviewer_response

async def interview_question_example():
    interview_service = InterviewService()
    
    # Get the next question
    question = await interview_service.get_next_question(interview_id)
    
    # Synthesize the question
    audio = await synthesize_interviewer_response(
        question.text, 
        persona=interview.interviewer_persona
    )
    
    # Return both text and audio
    return {
        "question_text": question.text,
        "question_audio": audio
    }
``` 