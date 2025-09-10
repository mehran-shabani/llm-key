# DRF Spectacular Schema Implementation

This directory contains the Django REST Framework Spectacular implementation for AnythingLLM API documentation.

## Files Overview

- `__init__.py` - Empty file to make this a Python package
- `schema.py` - Schema configuration, decorators, and common response schemas
- `urls.py` - URL patterns for schema endpoints
- `templates/swagger.html` - Custom Swagger UI template with dark theme support
- `static/swagger-dark.css` - Additional CSS for dark theme
- `requirements.txt` - Required Python packages
- `settings_example.py` - Django settings configuration example

## Endpoints

- `/api/schema/` - OpenAPI 3.0 schema (JSON)
- `/api/docs/` - Swagger UI interface
- `/api/redoc/` - ReDoc documentation interface

## Features

### Schema Configuration (`schema.py`)

- **Common Response Schemas**: Predefined schemas for authentication errors and success responses
- **Decorators**: Reusable decorators for authenticated and public endpoints
- **Parameter Definitions**: Standardized parameter definitions for common use cases

### Custom Swagger UI Template

- **Dark Theme Support**: Toggle between light and dark themes
- **Responsive Design**: Mobile-friendly interface
- **Custom Branding**: AnythingLLM logo and styling
- **Interactive Testing**: Built-in API testing capabilities

### Usage Examples

```python
from apps.api.schema.schema import auth_required_schema, public_schema

@auth_required_schema(
    summary="Get user profile",
    description="Retrieve the authenticated user's profile information"
)
def get_user_profile(request):
    # Your view logic here
    pass

@public_schema(
    summary="Health check",
    description="Check if the API is running"
)
def health_check(request):
    # Your view logic here
    pass
```

## Setup Instructions

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Add to Django settings:
   ```python
   INSTALLED_APPS = [
       'rest_framework',
       'drf_spectacular',
       'apps.api.schema',
   ]
   ```

3. Configure REST Framework and Spectacular settings (see `settings_example.py`)

4. Include URLs in your main `urls.py`:
   ```python
   urlpatterns = [
       path('api/', include('apps.api.schema.urls')),
   ]
   ```

## Migration from Existing Swagger

This implementation replaces the existing `server/swagger/` setup with a Django-native solution that:

- Automatically generates schemas from Django views
- Provides better integration with Django REST Framework
- Offers more customization options
- Maintains the same endpoint structure (`/api/schema/`, `/api/docs/`)

## Customization

- Modify `schema.py` to add new common schemas or decorators
- Update `templates/swagger.html` for UI customizations
- Adjust `static/swagger-dark.css` for theme modifications
- Configure additional settings in `SPECTACULAR_SETTINGS`