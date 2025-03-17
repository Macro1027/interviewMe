# API Documentation

## Overview

The API provides access to the project's AI capabilities including natural language processing, speech recognition, and emotion analysis.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.example.com`

## Authentication

All API endpoints require authentication. The API uses OAuth 2.0 with JWT tokens.

```
Authorization: Bearer <your_token>
```

## Endpoints

### Authentication

#### `POST /api/auth/token`

Get an access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### NLP

#### `POST /api/nlp/analyze`

Analyze text using NLP models.

**Request Body:**
```json
{
  "text": "string",
  "analysis_type": "sentiment | entity | intent | summarization",
  "model": "string" // optional
}
```

**Response:**
```json
{
  "analysis": {
    // Depends on analysis_type
  },
  "model_used": "string",
  "processing_time": "float" // seconds
}
```

### Speech Recognition

#### `POST /api/speech/transcribe`

Convert speech to text.

**Request Body:**
- Multipart form with audio file

**Response:**
```json
{
  "transcript": "string",
  "confidence": 0.95,
  "language_detected": "en"
}
```

### Voice Synthesis

#### `POST /api/speech/synthesize`

Generate speech from text.

**Request Body:**
```json
{
  "text": "string",
  "voice_id": "string", // optional
  "speed": 1.0, // optional
  "format": "mp3 | wav" // optional
}
```

**Response:**
- Audio file

### Emotion Analysis

#### `POST /api/emotion/analyze`

Analyze emotions in text or speech.

**Request Body:**
```json
{
  "text": "string", // optional if audio provided
  "audio": "base64-encoded-audio", // optional if text provided
  "detailed": false // optional
}
```

**Response:**
```json
{
  "emotions": {
    "primary": "string",
    "scores": {
      "happy": 0.1,
      "sad": 0.2,
      "angry": 0.05,
      "surprised": 0.05,
      "neutral": 0.6
    }
  },
  "confidence": 0.85
}
```

## Error Handling

All errors are returned with appropriate HTTP status codes and a JSON body:

```json
{
  "error": "string",
  "detail": "string",
  "code": "string",
  "timestamp": "string"
}
```

## Rate Limiting

API calls are limited to 100 requests per minute per API key. The following headers are included in all responses:

- `X-Rate-Limit-Limit`: Number of requests allowed per time window
- `X-Rate-Limit-Remaining`: Number of requests remaining in the current time window
- `X-Rate-Limit-Reset`: Time when the current rate limit window resets (UTC epoch seconds)
