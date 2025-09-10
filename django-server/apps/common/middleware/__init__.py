"""
Middleware utilities for Django applications.
Contains authentication and validation middleware.
"""

import os
import re
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .http import decode_jwt, create_error_response


class ValidatedRequestMiddleware(MiddlewareMixin):
    """
    Middleware for validating requests in single-user mode.
    Adapted from Node.js validatedRequest middleware.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request and validate authentication.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            JsonResponse with error if validation fails, None if valid
        """
        # Check if multi-user mode is enabled
        multi_user_mode = getattr(settings, 'MULTI_USER_MODE', False)
        if multi_user_mode:
            return None  # Skip validation in multi-user mode
        
        # Development passthrough or missing auth configuration
        if (settings.DEBUG or 
            not getattr(settings, 'AUTH_TOKEN', None) or 
            not getattr(settings, 'JWT_SECRET', None)):
            return None
        
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return create_error_response("No auth token found.", 401)
        
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return create_error_response("Invalid auth header format.", 401)
        
        decoded = decode_jwt(token)
        if not decoded or not decoded.get('p'):
            return create_error_response("Token expired or failed validation.", 401)
        
        # Validate password hash (simplified version)
        p_value = decoded.get('p')
        if not p_value or not re.match(r'\w{32}:\w{32}', p_value):
            return create_error_response("Token expired or failed validation.", 401)
        
        # Note: Full password validation with encryption would require 
        # implementing the EncryptionManager equivalent in Python
        return None


class ValidApiKeyMiddleware(MiddlewareMixin):
    """
    Middleware for validating API keys.
    Adapted from Node.js validApiKey middleware.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request and validate API key.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            JsonResponse with error if validation fails, None if valid
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return create_error_response("No valid api key found.", 403)
        
        try:
            bearer_key = auth_header.split(' ')[1]
        except IndexError:
            return create_error_response("No valid api key found.", 403)
        
        # Note: Full API key validation would require database lookup
        # This is a simplified version that checks for non-empty key
        if not bearer_key or len(bearer_key) < 10:
            return create_error_response("No valid api key found.", 403)
        
        return None


class ValidWorkspaceMiddleware(MiddlewareMixin):
    """
    Middleware for validating workspace access.
    Adapted from Node.js validWorkspace middleware.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request and validate workspace access.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            JsonResponse with error if validation fails, None if valid
        """
        # Extract workspace slug from URL
        workspace_slug = None
        if hasattr(request, 'resolver_match') and request.resolver_match:
            kwargs = request.resolver_match.kwargs
            workspace_slug = kwargs.get('slug')
        
        if not workspace_slug:
            return None  # No workspace validation needed
        
        # Note: Full workspace validation would require database lookup
        # This is a simplified version that validates slug format
        if not re.match(r'^[a-zA-Z0-9_-]+$', workspace_slug):
            return create_error_response("Invalid workspace slug format.", 400)
        
        return None


class MultiUserProtectedMiddleware(MiddlewareMixin):
    """
    Middleware for protecting multi-user endpoints.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request and validate multi-user mode requirements.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            JsonResponse with error if validation fails, None if valid
        """
        multi_user_mode = getattr(settings, 'MULTI_USER_MODE', False)
        if not multi_user_mode:
            return create_error_response("Multi-user mode is not enabled.", 403)
        
        return None


class FeatureFlagMiddleware(MiddlewareMixin):
    """
    Middleware for checking feature flags.
    """
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request and check feature flags.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            JsonResponse with error if feature is disabled, None if enabled
        """
        # Example feature flag check
        # This would be expanded based on specific feature requirements
        feature_flags = getattr(settings, 'FEATURE_FLAGS', {})
        
        # Check if specific features are enabled
        if not feature_flags.get('chat_history_viewable', True):
            if request.path.startswith('/api/chat-history'):
                return create_error_response("Chat history feature is disabled.", 403)
        
        return None