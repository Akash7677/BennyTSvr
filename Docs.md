# Text-to-Speech API Documentation

## Overview
This API provides text-to-speech functionality with GPT-4 integration, allowing for dynamic character-based responses with synchronized word timings. The service uses ElevenLabs for voice synthesis and maintains conversation history through sessions.

## Base URL
```
http://localhost:8000
```

## Authentication
API keys required:
- OpenAI API key for GPT-4
- ElevenLabs API key for voice synthesis

## Endpoints

### Generate Speech
Generates text and speech from input text with word-level timing information.

**Endpoint:** `/generate`
**Method:** POST

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | string | Yes      | - | The input text to process |
| profanity_level | integer | No       | 3 | Profanity level (0: None, 1: Mild, 2: Moderate, 3: High) |
| voice_id | string | Yes      | "542jzeOaLKbcpZhWfJDa" | ElevenLabs voice ID |
| stability | float | No       | 1.0 | Voice stability (0.0 to 1.0) |
| similarity_boost | float | No       | 0.5 | Voice similarity boost (0.0 to 1.0) |
| style | float | No       | 0.7 | Voice style (0.0 to 1.0) |
| use_speaker_boost | boolean | No       | true | Enable/disable speaker boost |
| session_id | string | No       | null | Session ID for conversation history |

#### Example Request
```json
{
    "text": "Tell me a joke!",
    "profanity_level": 3,
    "voice_id": "542jzeOaLKbcpZhWfJDa",
    "stability": 1.0,
    "similarity_boost": 0.5,
    "style": 0.7,
    "use_speaker_boost": true,
    "session_id": "user123"
}
```

#### Response Format
```json
{
    "text_response": "string",
    "audio_base64": "string",
    "words": ["string"],
    "word_start_times_seconds": [float],
    "word_end_times_seconds": [float]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| text_response | string | The generated text response from GPT-4 |
| audio_base64 | string | Base64 encoded MP3 audio data |
| words | array[string] | Array of words from the response |
| word_start_times_seconds | array[float] | Start times for each word in seconds |
| word_end_times_seconds | array[float] | End times for each word in seconds |

#### Example Response
```json
{
    "text_response": "Why don't dogs make good comedians? Because their jokes are too 'ruff'!",
    "audio_base64": "/+MYxAAAAANIAAAAAExBTUUzL...",
    "words": ["Why", "don't", "dogs", "make", "good", "comedians?", "Because", "their", "jokes", "are", "too", "'ruff'!"],
    "word_start_times_seconds": [0.0, 0.2, 0.4, 0.7, 0.9, 1.1, 1.5, 1.8, 2.0, 2.2, 2.4, 2.6],
    "word_end_times_seconds": [0.15, 0.35, 0.65, 0.85, 1.05, 1.4, 1.75, 1.95, 2.15, 2.35, 2.55, 2.9]
}
```

## Character Configuration
The API uses a character named "Benny," a talking dog with configurable personality traits. The character's responses are influenced by the profanity_level parameter:

- 0: Professional and formal responses
- 1: Mild humor and casual tone
- 2: Moderate humor and informal tone
- 3: Very humorous and informal tone with occasional mild language

## Session Management
- Sessions maintain conversation history for contextual responses
- Session timeout: 10 minutes of inactivity
- Session data includes conversation history and last activity timestamp

## Voice Settings

### Stability (0.0 - 1.0)
- Lower values: More expressive and variable output
- Higher values: More consistent and stable output

### Similarity Boost (0.0 - 1.0)
- Lower values: More creative voice variations
- Higher values: Closer to the original voice

### Style (0.0 - 1.0)
- Controls the style transfer intensity
- Higher values create more stylized speech

## Error Handling

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Successful response |
| 400 | Bad request - Invalid parameters |
| 401 | Unauthorized - Invalid API keys |
| 500 | Internal server error |

### Error Response Format
```json
{
    "detail": "Error message description"
}
```

## Client Implementation
Python client code is available for easy integration. Basic usage:

```python
from audio_stream_client import AudioStreamClient

client = AudioStreamClient(server_url="http://localhost:8000")

response = client.generate_response(
    text="Tell me a joke!",
    profanity_level=3,
    voice_id="542jzeOaLKbcpZhWfJDa",
    stability=1.0,
    similarity_boost=0.5,
    style=0.7
)

# Access response data
print(response['text_response'])
for word, start, end in zip(response['words'], 
                           response['word_start_times_seconds'],
                           response['word_end_times_seconds']):
    print(f"Word: {word}, Start: {start:.2f}s, End: {end:.2f}s")
```

## Rate Limiting
- Depends on your ElevenLabs and OpenAI API tier limits
- Implement appropriate request throttling in your client

## Best Practices
1. Maintain session IDs for conversational context
2. Handle audio streaming appropriately for better performance
3. Implement error handling and retries in client code
4. Monitor API usage to stay within rate limits
5. Cache responses when appropriate

## Dependencies
- FastAPI
- OpenAI
- ElevenLabs
- Pydantic
- SoundDevice (for client audio playback)
- PyDub (for audio processing)

## Setup Requirements
1. Python 3.7+
2. Required Python packages:
   ```bash
   pip install fastapi uvicorn openai elevenlabs pydantic sounddevice pydub
   ```
3. FFmpeg installation for audio processing
4. Valid API keys for OpenAI and ElevenLabs

## Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```