# AI Services Module

This module provides a collection of AI service implementations and a factory pattern for accessing them.

## Overview

The AI services module is designed with the following principles:

1. **Interface-Based Design**: All services implement common interfaces
2. **Factory Pattern**: Services are accessed through a factory to allow easy provider switching
3. **Provider Flexibility**: Support for multiple AI service providers
4. **Configuration-Driven**: Service selection based on environment configuration

## Available Services

### Completion Services

Text generation services for creating interview questions, responses, and other text content.

- **OpenAI** (`OpenAIService`): Uses OpenAI's GPT models
- **Perplexity** (`PerplexityService`): Uses Perplexity API for text completions

### Future Services (Coming Soon)

- **Embedding Services**: For vector embeddings and semantic search
- **Speech Recognition Services**: For converting speech to text
- **Speech Synthesis Services**: For converting text to speech
- **Sentiment Analysis Services**: For analyzing emotions in text/speech

## How to Use

### 1. Configure Environment Variables

Set the following environment variables in your `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANIZATION=your_openai_org_id

# Perplexity
PERPLEXITY_API_KEY=your_perplexity_api_key

# Provider Selection
COMPLETION_PROVIDER=perplexity  # Options: openai, perplexity
```

### 2. Setting the Perplexity API Key

You can use the helper script to set your Perplexity API key:

```bash
python -m src.ai.examples.set_perplexity_api_key YOUR_API_KEY_HERE
```

### 3. Using the Completion Service

```python
from src.ai.factory import get_completion_service

# Get the default provider (from environment settings)
completion_service = get_completion_service()

# Or specify a provider explicitly
completion_service = get_completion_service(provider="perplexity")

# Generate a completion
result = await completion_service.generate_completion(
    prompt="Generate an interview question about Python.",
    max_tokens=200
)

# Generate a chat completion
messages = [
    {"role": "system", "content": "You are an expert interviewer."},
    {"role": "user", "content": "Ask me a question about microservices."}
]
result = await completion_service.generate_chat_completion(
    messages=messages,
    max_tokens=300
)
```

### 4. Running the Example

Try the example script to test the Perplexity service:

```bash
python -m src.ai.examples.perplexity_example
```

## Adding New Service Providers

To add a new service provider:

1. Create a new implementation class that follows the appropriate interface
2. Register the implementation in `factory.py`
3. Update the environment variable settings in `config.py`

## Best Practices

- Always use the factory pattern to get service instances
- Handle potential exceptions from service methods
- Configure fallback mechanisms for critical operations
- Use environment variables for API keys and provider selection 