# Text Generation Module

This module provides text generation capabilities for the AI Interview Simulation Platform using Large Language Models (LLMs). It supports multiple LLM providers with a unified interface.

## Features

- Unified API for multiple language model providers
- Support for completion and chat-based API patterns
- Interview-specific text generation utilities
- Automatic fallback mechanisms
- Configuration-based provider customization
- Robust error handling and logging

## Supported Providers

Currently, the following providers are supported:

- **Perplexity AI** (Default): Uses the Perplexity API for high-quality text generation
- **Hugging Face**: Uses Hugging Face Inference API with models like Mixtral and Llama 2

## Usage

### Basic Text Generation

```python
from src.ai.text_generation import TextGenerationService

# Create a service instance (will use default provider from settings)
service = TextGenerationService()

# Generate a text completion
response = await service.generate_completion(
    prompt="Explain what a RESTful API is.",
    max_tokens=150
)
print(response)

# Generate a chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What are the key features of Python?"}
]
response = await service.generate_chat_completion(
    messages=messages,
    max_tokens=200
)
print(response)
```

### Interview-Specific Utilities

The module provides high-level functions specifically for interview simulations:

```python
from src.ai.text_generation import (
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)

# Generate an interview question
question = await generate_interview_question(
    topic="Python Programming",
    difficulty="intermediate"
)

# Evaluate a candidate's answer (returns structured feedback)
evaluation = await evaluate_interview_answer(
    question="What is dependency injection?",
    answer="Dependency injection is a design pattern where dependencies are passed into an object rather than created inside it."
)

# Generate a follow-up question based on a previous answer
follow_up = await generate_follow_up_question(
    question="Explain RESTful API design.",
    answer="RESTful APIs use HTTP methods like GET, POST, PUT, and DELETE to interact with resources."
)
```

## Configuration

The module can be configured via YAML files in the `config` directory:

- `perplexity.yaml`: Settings for the Perplexity API
- `huggingface.yaml`: Settings for the Hugging Face API

You can customize API endpoints, models, generation parameters, and fallback settings.

Additionally, these environment variables can be used to configure the service:

- `LLM_PROVIDER`: The default provider to use (e.g., "perplexity" or "huggingface")
- `PERPLEXITY_API_KEY`: API key for Perplexity AI
- `PERPLEXITY_MODEL`: Default model for Perplexity (e.g., "pplx-70b-online")
- `HUGGINGFACE_API_KEY`: API key for Hugging Face
- `HUGGINGFACE_MODEL`: Default model for Hugging Face (e.g., "mistralai/Mixtral-8x7B-Instruct-v0.1")

## Error Handling and Fallbacks

The service implements robust error handling and fallback mechanisms:

1. If a provider fails with a temporary error, it will automatically retry the request.
2. If using `use_fallback=True`, the service will attempt to use an alternative provider when the primary provider fails.
3. All errors are properly logged for monitoring and debugging.

## Testing

The module includes comprehensive tests in the `tests` directory:

- `test_perplexity.py`: Tests for the Perplexity API integration
- `test_huggingface.py`: Tests for the Hugging Face API integration

Run the tests using pytest:

```
pytest src/ai/text_generation/tests
```