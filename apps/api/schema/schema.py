"""
DRF Spectacular schema configuration for AnythingLLM API
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers


class InvalidAPIKeySerializer(serializers.Serializer):
    """Serializer for invalid API key responses"""
    message = serializers.CharField(default="Invalid API Key")


# Common response schemas
INVALID_API_KEY_RESPONSE = {
    '403': {
        'description': 'Forbidden - Invalid API Key',
        'content': {
            'application/json': {
                'schema': InvalidAPIKeySerializer
            }
        }
    }
}

AUTHENTICATED_RESPONSE = {
    '200': {
        'description': 'Valid auth token was found',
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'authenticated': {
                            'type': 'boolean',
                            'example': True
                        }
                    }
                }
            }
        }
    }
}

# Common parameters
AUTHORIZATION_HEADER = OpenApiParameter(
    name='Authorization',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    description='Bearer token for API authentication',
    required=True
)

# Schema decorators for common patterns
def auth_required_schema(summary=None, description=None, **kwargs):
    """Decorator for endpoints that require authentication"""
    return extend_schema(
        summary=summary,
        description=description,
        parameters=[AUTHORIZATION_HEADER],
        responses={
            **AUTHENTICATED_RESPONSE,
            **INVALID_API_KEY_RESPONSE,
            **kwargs.get('responses', {})
        },
        **{k: v for k, v in kwargs.items() if k != 'responses'}
    )


def public_schema(summary=None, description=None, **kwargs):
    """Decorator for public endpoints"""
    return extend_schema(
        summary=summary,
        description=description,
        **kwargs
    )