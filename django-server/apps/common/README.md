# Django Common Utilities

This package contains common utilities ported from the Node.js server to Django applications. It includes provider-agnostic utilities and OpenAI-specific helpers.

## Structure

```
apps/common/
├── __init__.py              # Package initialization
├── logger.py               # Logging utilities
├── http.py                 # HTTP utilities (JWT, auth, requests)
├── validation.py           # Validation utilities
├── errors.py               # Error handling and custom exceptions
├── file_utils.py           # File handling utilities
├── pagination.py           # Pagination helpers
├── openai_utils.py         # OpenAI-specific utilities
└── middleware/             # Django middleware
    └── __init__.py         # Middleware utilities
```

## Features

### Logger (`logger.py`)
- Singleton logger class for consistent logging
- Production and development logging configurations
- Colorized console output for development
- Structured logging for production

### HTTP Utilities (`http.py`)
- JWT token creation and validation
- Request/response helpers
- Authorization header parsing
- URL validation
- JSON parsing with fallback options

### Validation (`validation.py`)
- Email validation
- Password strength validation
- Required field validation
- String length validation
- Numeric range validation
- Slug and UUID validation
- Filename sanitization
- Basic JSON schema validation

### Error Handling (`errors.py`)
- Custom exception classes for different error types
- Standardized error response creation
- API exception handling
- Validation error handling

### File Utilities (`file_utils.py`)
- File path normalization and security
- Filename sanitization
- File hash calculation
- File size and type validation
- Directory management
- Temporary file cleanup
- File information extraction

### Pagination (`pagination.py`)
- Django queryset pagination
- List pagination
- Pagination parameter extraction
- Pagination links generation
- Offset/limit conversion

### OpenAI Utilities (`openai_utils.py`)
- OpenAI LLM provider wrapper
- OpenAI embedding provider
- Chat completion handling
- Model validation
- Prompt construction

### Middleware (`middleware/`)
- Request validation middleware
- API key validation middleware
- Workspace validation middleware
- Multi-user protection middleware
- Feature flag middleware

## Usage Examples

### Logger
```python
from apps.common.logger import get_logger, log_info, log_error

logger = get_logger()
logger.info("Application started")

# Or use convenience functions
log_info("User logged in", user_id=123)
log_error("Database connection failed")
```

### HTTP Utilities
```python
from apps.common.http import make_jwt, decode_jwt, create_error_response

# Create JWT token
token = make_jwt({"user_id": 123, "username": "john"})

# Decode JWT token
payload = decode_jwt(token)

# Create error response
response = create_error_response("Invalid request", 400)
```

### Validation
```python
from apps.common.validation import validate_email, validate_required_fields

# Validate email
is_valid = validate_email("user@example.com")

# Validate required fields
data = {"name": "John", "email": "john@example.com"}
result = validate_required_fields(data, ["name", "email", "password"])
if not result['valid']:
    print(f"Missing fields: {result['missing_fields']}")
```

### Error Handling
```python
from apps.common.errors import ValidationError, NotFoundError, handle_api_exception

try:
    # Some operation
    raise ValidationError("Invalid email format", field="email")
except ValidationError as e:
    response = handle_api_exception(e)
```

### File Utilities
```python
from apps.common.file_utils import normalize_path, sanitize_filename, get_file_info

# Normalize file path
safe_path = normalize_path("../../../etc/passwd")  # Raises ValueError

# Sanitize filename
clean_name = sanitize_filename("file<>name.txt")  # "file__name.txt"

# Get file information
info = get_file_info("/path/to/file.txt")
```

### Pagination
```python
from apps.common.pagination import paginate_queryset, get_pagination_params

# Get pagination parameters from request
page, page_size = get_pagination_params(request)

# Paginate queryset
result = paginate_queryset(queryset, page, page_size)
```

### OpenAI Utilities
```python
from apps.common.openai_utils import OpenAiLLM, OpenAiEmbedder

# Initialize OpenAI LLM
llm = OpenAiLLM(model_preference="gpt-4o")

# Get chat completion
messages = [{"role": "user", "content": "Hello!"}]
response = await llm.get_chat_completion(messages)

# Initialize OpenAI Embedder
embedder = OpenAiEmbedder()
embeddings = await embedder.embed_text_input("Hello world")
```

### Middleware
```python
# In settings.py
MIDDLEWARE = [
    'apps.common.middleware.ValidatedRequestMiddleware',
    'apps.common.middleware.ValidApiKeyMiddleware',
    # ... other middleware
]
```

## Configuration

### Environment Variables
- `JWT_SECRET`: Secret key for JWT token signing
- `OPEN_AI_KEY`: OpenAI API key
- `OPEN_MODEL_PREF`: Preferred OpenAI model
- `EMBEDDING_MODEL_PREF`: Preferred embedding model
- `STORAGE_DIR`: Base directory for file storage
- `MULTI_USER_MODE`: Enable multi-user mode
- `AUTH_TOKEN`: Authentication token for single-user mode

### Django Settings
```python
# settings.py
JWT_SECRET = os.getenv('JWT_SECRET')
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
OPEN_MODEL_PREF = os.getenv('OPEN_MODEL_PREF', 'gpt-4o')
EMBEDDING_MODEL_PREF = os.getenv('EMBEDDING_MODEL_PREF', 'text-embedding-ada-002')
STORAGE_DIR = os.getenv('STORAGE_DIR', '/tmp/storage')
MULTI_USER_MODE = os.getenv('MULTI_USER_MODE', 'false').lower() == 'true'
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
```

## Dependencies

- Django (3.2+)
- PyJWT (for JWT handling)
- Python standard library modules

## Notes

- This is a minimal, dependency-light implementation
- OpenAI utilities are simplified and would need actual OpenAI library integration
- Middleware implementations are basic and may need customization for specific use cases
- File utilities include security measures for path traversal prevention
- All utilities are designed to be provider-agnostic except for OpenAI-specific ones