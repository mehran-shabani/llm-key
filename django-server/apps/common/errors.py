"""
Error handling utilities for Django applications.
Contains custom exceptions and error response helpers.
"""

from typing import Any, Dict, Optional

from django.http import JsonResponse


class APIException(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        """
        Initialize API exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            details: Additional error details
        """
        self.field = field
        error_details = details or {}
        if field:
            error_details['field'] = field
        
        super().__init__(message, 400, error_details)


class AuthenticationError(APIException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 401, details)


class AuthorizationError(APIException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        """
        Initialize authorization error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 403, details)


class NotFoundError(APIException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        """
        Initialize not found error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 404, details)


class ConflictError(APIException):
    """Exception for resource conflict errors."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        """
        Initialize conflict error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 409, details)


class RateLimitError(APIException):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 429, details)


class ServerError(APIException):
    """Exception for server errors."""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        """
        Initialize server error.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message, 500, details)


def create_error_response(message: str, status_code: int = 400, 
                         details: Optional[Dict[str, Any]] = None) -> JsonResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JsonResponse with error information
    """
    error_data = {
        'error': message,
        'status_code': status_code
    }
    
    if details:
        error_data['details'] = details
    
    return JsonResponse(error_data, status=status_code)


def handle_api_exception(exception: APIException) -> JsonResponse:
    """
    Handle API exception and create appropriate response.
    
    Args:
        exception: APIException instance
        
    Returns:
        JsonResponse with error information
    """
    return create_error_response(
        exception.message,
        exception.status_code,
        exception.details
    )


def handle_validation_error(errors: Dict[str, Any]) -> JsonResponse:
    """
    Handle validation errors and create appropriate response.
    
    Args:
        errors: Dictionary of validation errors
        
    Returns:
        JsonResponse with validation errors
    """
    return JsonResponse({
        'error': 'Validation failed',
        'status_code': 400,
        'validation_errors': errors
    }, status=400)


def handle_unexpected_error(exception: Exception) -> JsonResponse:
    """
    Handle unexpected errors and create appropriate response.
    
    Args:
        exception: Unexpected exception
        
    Returns:
        JsonResponse with generic error message
    """
    return create_error_response(
        "An unexpected error occurred",
        500,
        {'exception_type': type(exception).__name__}
    )