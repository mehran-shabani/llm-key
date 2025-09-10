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
## Speech-to-Text (STT)

### POST /api/stt/

Transcribe audio to text using OpenAI Whisper.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `audio` (file, required): Audio file to transcribe
  - `model` (string, optional): Model to use (default: "whisper-1")

**Response:**
```json
{
  "transcript": "Transcribed text from audio",
  "model": "whisper-1"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/stt/ \
  -F "audio=@audio_file.mp3" \
  -F "model=whisper-1"
```

**Available Models:**
- `whisper-1` (default)

**Error Responses:**
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Transcription failed
<!-- END: STT -->

<!-- BEGIN: TTS -->
## Text-to-Speech (TTS)

### POST /api/tts/

Convert text to speech using OpenAI TTS.

**Request:**
- Content-Type: `application/json`
- Parameters:
  - `text` (string, required): Text to convert to speech
  - `model` (string, optional): Model to use (default: "tts-1")
  - `voice` (string, optional): Voice to use (default: "alloy")

**Response:**
```json
{
  "audio_base64": "base64_encoded_audio_data",
  "model": "tts-1",
  "voice": "alloy"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/tts/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "model": "tts-1",
    "voice": "alloy"
  }'
```

**Available Models:**
- `tts-1` (default)
- `tts-1-hd`

**Available Voices:**
- `alloy` (default)
- `echo`
- `fable`
- `onyx`
- `nova`
- `shimmer`

**Error Responses:**
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Speech synthesis failed
<!-- END: TTS -->

<!-- BEGIN: CONVERSATION -->
<!-- END: CONVERSATION -->

<!-- BEGIN: SCHEMA -->
<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
<!-- END: JOBS -->
