# AnythingLLM Django Server

This is the Django REST Framework implementation of the AnythingLLM server endpoints.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser:
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/api/docs/
- Schema: http://localhost:8000/api/schema/

## Apps Structure

- `apps/coredb`: Core database models based on Prisma schema
- `apps/api_auth`: Authentication endpoints
- `apps/api_admin`: Admin management endpoints  
- `apps/api_system`: System settings endpoints

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_BASE_URL`: OpenAI base URL (default: https://api.openai.com/v1)

## Authentication

All API endpoints require authentication via API key in the Authorization header:
```
Authorization: Bearer your-api-key-here
```