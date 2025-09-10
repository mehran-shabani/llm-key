# Django settings configuration for DRF Spectacular
# Add these settings to your Django project's settings.py

INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'drf_spectacular',
    'apps.api.schema',  # Your schema app
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# DRF Spectacular configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'AnythingLLM Developer API',
    'DESCRIPTION': 'API endpoints that enable programmatic reading, writing, and updating of your AnythingLLM instance.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVERS': [
        {'url': '/api', 'description': 'API Server'},
    ],
    'SECURITY': [
        {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'Authentication endpoints'},
        {'name': 'Admin', 'description': 'Administrative endpoints'},
        {'name': 'System', 'description': 'System information endpoints'},
        {'name': 'Workspaces', 'description': 'Workspace management'},
        {'name': 'Chats', 'description': 'Chat and conversation endpoints'},
        {'name': 'Documents', 'description': 'Document management'},
        {'name': 'Files', 'description': 'File upload and management'},
        {'name': 'LLM', 'description': 'Large Language Model endpoints'},
        {'name': 'Embedding', 'description': 'Text embedding endpoints'},
        {'name': 'Image', 'description': 'Image processing endpoints'},
        {'name': 'STT', 'description': 'Speech-to-Text endpoints'},
        {'name': 'TTS', 'description': 'Text-to-Speech endpoints'},
        {'name': 'Conversation', 'description': 'Conversation management'},
        {'name': 'Jobs', 'description': 'Background job management'},
    ],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
        'tryItOutEnabled': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
    },
}

# URL configuration
# Add to your main urls.py:
# urlpatterns = [
#     # ... other patterns
#     path('api/', include('apps.api.schema.urls')),
# ]