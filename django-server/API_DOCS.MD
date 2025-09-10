# API_DOCS

<!-- BEGIN: AUTH -->
<!-- END: AUTH -->

<!-- BEGIN: ADMIN -->
<!-- END: ADMIN -->

<!-- BEGIN: SYSTEM -->
<!-- END: SYSTEM -->

<!-- BEGIN: WORKSPACES -->
<!-- END: WORKSPACES -->

<!-- BEGIN: CHATS -->
<!-- END: CHATS -->

<!-- BEGIN: DOCUMENTS -->
<!-- END: DOCUMENTS -->

<!-- BEGIN: FILES -->
<!-- END: FILES -->

<!-- BEGIN: LLM -->
<!-- END: LLM -->

<!-- BEGIN: EMBEDDING -->
<!-- END: EMBEDDING -->

<!-- BEGIN: IMAGE -->
<!-- END: IMAGE -->

<!-- BEGIN: STT -->
<!-- END: STT -->

<!-- BEGIN: TTS -->
<!-- END: TTS -->

<!-- BEGIN: CONVERSATION -->
## Voice Conversation API

### POST /api/conversation/

Process synchronous voice conversation chain: STT → LLM → TTS

**Input:**
- `audio` (multipart file, required): Audio file for speech-to-text
  - Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
  - Maximum size: 25MB
- `stt_model` (string, optional): STT model override (default: whisper-1)
- `text_model` (string, optional): LLM model override (default: gpt-4o)
- `tts_model` (string, optional): TTS model override (default: tts-1)

**Headers:**
- `X-OpenAI-API-Key` (required): OpenAI API key
- `X-OpenAI-Base-URL` (optional): Custom OpenAI base URL
- Alternative: `Authorization: Bearer <api_key>`

**Output:**
```json
{
  "transcript": "string",
  "text_response": "string", 
  "audio": "base64_encoded_audio",
  "models_used": {
    "stt": "whisper-1",
    "text": "gpt-4o",
    "tts": "tts-1"
  },
  "success": true,
  "errors": []
}
```

**Response Codes:**
- `200 OK`: Complete success
- `206 Partial Content`: Partial success with errors
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing API key
- `500 Internal Server Error`: Server error

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/conversation/ \
  -H "X-OpenAI-API-Key: your-api-key" \
  -F "audio=@audio_file.wav" \
  -F "stt_model=whisper-1" \
  -F "text_model=gpt-4o-mini" \
  -F "tts_model=tts-1-hd"
```

**Pipeline:**
1. **STT**: Convert audio to text using OpenAI Whisper
2. **LLM**: Generate text response using OpenAI GPT models
3. **TTS**: Convert response to speech using OpenAI TTS

**Model Registry:**
Models are validated against MODEL_LIST.MD configuration. Invalid models fallback to defaults.
<!-- END: CONVERSATION -->

<!-- BEGIN: SCHEMA -->
<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
<!-- END: JOBS -->
