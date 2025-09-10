# STT and TTS Implementation

This Django project implements Speech-to-Text (STT) and Text-to-Speech (TTS) functionality using OpenAI's Whisper and TTS models.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### STT (Speech-to-Text)
- **POST** `/api/stt/`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `audio` (file, required): Audio file to transcribe
  - `model` (string, optional): Model to use (default: "whisper-1")

### TTS (Text-to-Speech)
- **POST** `/api/tts/`
- **Content-Type**: `application/json`
- **Parameters**:
  - `text` (string, required): Text to convert to speech
  - `model` (string, optional): Model to use (default: "tts-1")
  - `voice` (string, optional): Voice to use (default: "alloy")

## Available Models

The implementation uses models from `MODEL_LIST.MD`:

- **STT**: `whisper-1` (default)
- **TTS**: `tts-1` (default), `tts-1-hd`

## Available Voices

- `alloy` (default)
- `echo`
- `fable`
- `onyx`
- `nova`
- `shimmer`

## Project Structure

```
django-server/
├── apps/
│   ├── stt/
│   │   ├── __init__.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── tts/
│       ├── __init__.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── config/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── MODEL_LIST.MD
└── API_DOCS.MD
```