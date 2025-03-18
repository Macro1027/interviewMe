# AI Module

This module provides AI capabilities for the interview platform using a simplified, consolidated approach.

## Overview

The AI module has been completely streamlined:

1. **Consolidated LLM File**: All language model functionality is in a single file
2. **Direct API Access**: Uses Perplexity API directly for text generation
3. **No Unnecessary Abstractions**: Removed interfaces and factory patterns
4. **Higher-Level Utilities**: Includes interview-specific functions

## LLM Capabilities

The language model service in `llm.py` provides:

- **Basic Text Generation**: Generate completions for prompts
- **Chat-Based Generation**: Support for multi-turn conversations
- **Token Counting**: For tracking API usage
- **Interview Utilities**: Functions for generating questions, evaluating answers, etc.

## How to Use

### 1. Configure Environment Variables

Set the following in your `.env` file:

```bash
# Required for LLM functionality
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### 2. Basic LLM Usage

```python
from src.ai.llm import get_llm_service

# Get the LLM service
llm = get_llm_service()

# Generate completion
result = await llm.generate_completion(
    prompt="Generate an interview question about Python.",
    max_tokens=200
)

# Generate chat completion
messages = [
    {"role": "system", "content": "You are an expert interviewer."},
    {"role": "user", "content": "Ask me about microservices."}
]
result = await llm.generate_chat_completion(
    messages=messages,
    max_tokens=300
)
```

### 3. Higher-Level Interview Functions

```python
from src.ai.llm import (
    generate_interview_question,
    evaluate_interview_answer,
    generate_follow_up_question
)

# Generate an interview question
question = await generate_interview_question(
    topic="Data Structures", 
    difficulty="hard"
)

# Evaluate a candidate's answer
evaluation = await evaluate_interview_answer(
    question="What are binary search trees?",
    answer="Binary search trees are data structures that allow fast lookup, insertion, and deletion..."
)

# Generate follow-up question
follow_up = await generate_follow_up_question(
    question="What are binary search trees?",
    answer="Binary search trees are data structures that allow fast lookup, insertion, and deletion..."
)
```

### 4. Running the Example

Try the example script to see all capabilities:

```bash
python -m src.ai.examples.llm_example
```

## Other AI Functions

Additional AI capabilities like speech recognition, synthesis, and sentiment analysis will be added in the future following this same simplified approach.

## Best Practices

- Handle exceptions from API calls
- Consider implementing local caching for frequent requests
- Use higher-level functions for interview-specific tasks 