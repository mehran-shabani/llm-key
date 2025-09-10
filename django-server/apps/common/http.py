"""
HTTP utilities for Django applications.
Contains JWT handling, authentication, and request/response utilities.
"""

import json
import os
import re
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

import jwt
from django.conf import settings
from django.http import HttpRequest, JsonResponse


def safe_json_parse(json_string: Optional[str], fallback: Any = None) -> Any:
    """
    Safely parse JSON string with fallback options.
    
    Args:
        json_string: JSON string to parse
        fallback: Fallback value if parsing fails
        
    Returns:
        Parsed JSON or fallback value
    """
    if json_string is None:
        return fallback
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        pass
    
    # Try to repair malformed JSON
    if json_string.startswith(('{', '[')):
        try:
            # Simple JSON repair for common issues
            repaired = json_string.replace("'", '"')  # Replace single quotes
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    
    return fallback


def make_jwt(info: Dict[str, Any] = None, expiry: str = "30d") -> str:
    """
    Create a JWT with the given info and expiry.
    
    Args:
        info: The info to include in the JWT
        expiry: The expiry time for the JWT (default: 30 days)
        
    Returns:
        The JWT token
        
    Raises:
        ValueError: If JWT_SECRET is not set
    """
    if not info:
        info = {}
    
    jwt_secret = getattr(settings, 'JWT_SECRET', os.getenv('JWT_SECRET'))
    if not jwt_secret:
        raise ValueError("Cannot create JWT as JWT_SECRET is unset.")
    
    return jwt.encode(info, jwt_secret, algorithm="HS256")


def decode_jwt(jwt_token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        jwt_token: The JWT token to decode
        
    Returns:
        Decoded JWT payload or empty dict with null values
    """
    jwt_secret = getattr(settings, 'JWT_SECRET', os.getenv('JWT_SECRET'))
    if not jwt_secret:
        return {"p": None, "id": None, "username": None}
    
    try:
        return jwt.decode(jwt_token, jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return {"p": None, "id": None, "username": None}


def parse_auth_header(header_value: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Parse authorization header and return appropriate header dict.
    
    Args:
        header_value: The header name (e.g., "Authorization")
        api_key: The API key value
        
    Returns:
        Dictionary with header name and value
    """
    if header_value is None or api_key is None:
        return {}
    
    if header_value == "Authorization":
        return {"Authorization": f"Bearer {api_key}"}
    
    return {header_value: api_key}


def is_valid_url(url_string: str = "") -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url_string: URL string to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        parsed = urlparse(url_string)
        return parsed.scheme in ('http', 'https')
    except Exception:
        return False


def to_valid_number(number: Any, fallback: Any = None) -> Union[int, float, Any]:
    """
    Convert a value to a valid number.
    
    Args:
        number: Value to convert
        fallback: Fallback value if conversion fails
        
    Returns:
        Converted number or fallback value
    """
    try:
        return float(number)
    except (ValueError, TypeError):
        return fallback


def get_request_body(request: HttpRequest) -> Dict[str, Any]:
    """
    Extract request body from Django request.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        Parsed request body as dictionary
    """
    if hasattr(request, 'body') and request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {}
    return getattr(request, 'data', {})


def get_query_params(request: HttpRequest) -> Dict[str, Any]:
    """
    Extract query parameters from Django request.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        Query parameters as dictionary
    """
    return dict(request.GET)


def create_error_response(message: str, status_code: int = 400) -> JsonResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        JsonResponse with error message
    """
    return JsonResponse({"error": message}, status=status_code)


def create_success_response(data: Any = None, message: str = "Success") -> JsonResponse:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        JsonResponse with success message and data
    """
    response_data = {"message": message}
    if data is not None:
        response_data["data"] = data
    return JsonResponse(response_data)