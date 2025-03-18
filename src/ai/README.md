# AI Services Module

This module provides AI services for the interview platform using a simplified, direct approach.

## Overview

The AI services module has been simplified to use specific implementations directly rather than a factory pattern:

1. **Direct Service Access**: Services are accessed through simple getter functions
2. **Single Provider**: Each AI capability uses a specific provider
3. **Simplified Configuration**: Configuration focuses only on the APIs being used

## Available Services

### LLM Service (Perplexity)

The Language Model service provides text generation capabilities using Perplexity API:

- Text completions for generating interview questions
- Chat completions for multi-turn interactions
- Token counting for estimating usage

### Future Services (Coming Soon)

- **Speech Recognition**: For converting speech to text
- **Speech Synthesis**: For converting text to speech
- **Sentiment Analysis**: For analyzing emotions in text/speech
- **Embedding Service**: For vector embeddings and semantic search

## How to Use

### 1. Configure Environment Variables

Set the following environment variables in your `.env` file:

```bash
# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key
PERPLEXITY_MODEL=pplx-70b-online  # Optional - defaults to pplx-70b-online
```

### 2. Using the LLM Service

```python
from src.ai.services import get_llm_service

# Get the LLM service
llm_service = get_llm_service()

# Generate a completion
result = await llm_service.generate_completion(
    prompt="Generate an interview question about Python.",
    max_tokens=200
)

# Generate a chat completion
messages = [
    {"role": "system", "content": "You are an expert interviewer."},
    {"role": "user", "content": "Ask me a question about microservices."}
]
result = await llm_service.generate_chat_completion(
    messages=messages,
    max_tokens=300
)
```

### 3. Running the Example

Try the example script to test the LLM service:

```bash
python -m src.ai.examples.llm_example
```

## Setting the Perplexity API Key

You can manually add your Perplexity API key to the `.env` file:

```
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

## Best Practices

- Handle potential exceptions from service methods
- Consider implementing local caching for frequent requests
- Use environment variables for API keys 