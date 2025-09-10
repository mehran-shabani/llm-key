# AnythingLLM Django Server

A modern Django REST Framework implementation of the AnythingLLM backend, providing a powerful LLM chat application with document processing, embeddings, and multi-user support.

## 🚀 Overview

This is a complete rewrite of the original Node.js/Express AnythingLLM server in Django, maintaining full API compatibility while leveraging Django's robust ecosystem and architectural patterns.

### Key Features

- **Multi-User Support**: Role-based access control with admin, manager, and default user roles
- **Workspace Management**: Isolated environments for different projects and teams
- **Document Processing**: Upload, parse, and vectorize documents for RAG
- **Real-time Chat**: WebSocket support for streaming responses
- **Embeddings**: Embeddable chat widgets for external websites
- **API Keys**: Developer API access and browser extension support
- **Event Logging**: Comprehensive audit trail and telemetry

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or SQLite for development)
- Redis 6+ (for WebSockets and caching)
- Node.js 18+ (for frontend assets, optional)

## 🛠️ Installation

### 1. Clone the Repository

```bash
cd django_server
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy sample environment file
cp .env.sample .env

# Edit .env with your configuration
nano .env
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (optional)
python manage.py loaddata initial_data.json
```

### 5. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 6. Run Development Server

```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker (optional)
celery -A anythingllm worker -l info

# Start Celery beat scheduler (optional)
celery -A anythingllm beat -l info
```

## 🐳 Docker Setup

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f
```

### Docker Services

- **web**: Django application server
- **db**: PostgreSQL database
- **redis**: Redis for caching and WebSockets
- **celery**: Background task worker
- **celerybeat**: Scheduled task runner

## 📁 Project Structure

```
django_server/
├── anythingllm/          # Main Django project settings
│   ├── settings.py       # Django configuration
│   ├── urls.py          # URL routing
│   ├── asgi.py          # ASGI configuration for WebSockets
│   └── wsgi.py          # WSGI configuration
├── authentication/       # User authentication and management
├── workspaces/          # Workspace management
├── documents/           # Document upload and processing
├── chats/              # Chat functionality and WebSockets
├── embeddings/         # Embeddable widget configuration
├── system_settings/    # System configuration and logging
├── api_keys/          # API key and invitation management
├── storage/           # File storage directory
├── static/            # Static files
├── templates/         # HTML templates
├── requirements.txt   # Python dependencies
├── docker-compose.yml # Docker orchestration
└── manage.py         # Django management script
```

## 🔧 Configuration

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `MULTI_USER_MODE` | Enable multi-user features | `True` |
| `LLM_PROVIDER` | LLM provider (openai, anthropic, etc.) | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | Required for OpenAI |
| `VECTOR_DB` | Vector database (pinecone, qdrant, etc.) | `pinecone` |

### LLM Providers Supported

- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Cohere
- Ollama (local models)
- Custom providers via adapter pattern

### Vector Databases Supported

- Pinecone
- Qdrant
- ChromaDB
- Weaviate
- LanceDB

## 🔌 API Documentation

### Interactive API Documentation

Once the server is running, access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

### Authentication

The API uses JWT tokens for authentication:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use the returned access token in subsequent requests
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/workspaces/
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
python manage.py test authentication
```

### Test Coverage

Current test coverage target: ≥80%

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/ping/
# Returns: {"online": true}
```

### System Status

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/system/status/
```

## 🔄 Migration from Original Server

### Data Migration

1. Export data from the original Node.js server
2. Use the provided migration scripts in `migrations/`
3. Import data into Django database

### API Compatibility

The Django server maintains full API compatibility with the original Node.js implementation. Existing clients should work without modification.

### Feature Parity

All features from the original server have been implemented:
- ✅ User authentication and management
- ✅ Workspace management
- ✅ Document processing
- ✅ Chat functionality
- ✅ WebSocket support
- ✅ Embedding widgets
- ✅ API keys
- ✅ Event logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## 🙏 Acknowledgments

- Original AnythingLLM team for the Node.js implementation
- Django and Django REST Framework communities
- All contributors and users of this project