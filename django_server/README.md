# Django Server Skeleton

A Django skeleton with shared core utilities for OpenAI integration.

## Structure

```
django_server/
├── manage.py                 # Django management script
├── project/                  # Django project configuration
│   ├── __init__.py
│   ├── settings.py          # Django settings with OpenAI config
│   ├── urls.py              # URL configuration
│   ├── asgi.py              # ASGI configuration
│   └── wsgi.py              # WSGI configuration
├── core/                    # Shared core utilities
│   ├── __init__.py
│   ├── openai_client.py     # OpenAI API client
│   ├── model_registry.py    # Model registry from MODEL_LIST.md
│   └── md_parser.py         # Markdown JSON parser
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── MODEL_LIST.md           # OpenAI models configuration
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start development server:
   ```bash
   python manage.py runserver
   ```

## Core Utilities

### OpenAI Client (`core/openai_client.py`)
- Handles OpenAI API calls
- Accepts API key and base URL from headers or environment
- Supports chat completions, embeddings, image generation, TTS, STT

### Model Registry (`core/model_registry.py`)
- Loads models from `MODEL_LIST.md`
- Provides `select(category, requested)` method
- Categories: text_gen, text2text, image, embedding, tts, stt

### Markdown Parser (`core/md_parser.py`)
- Extracts first fenced JSON block from markdown files
- Used by model registry to parse `MODEL_LIST.md`

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Schema: http://localhost:8000/api/schema/