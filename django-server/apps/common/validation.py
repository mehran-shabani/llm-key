"""
Validation utilities for Django applications.
Contains common validation functions and helpers.
"""

import os
import re
from typing import Any, Dict, List, Optional, Union


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str, min_length: int = 8) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        
    Returns:
        Dictionary with validation result and details
    """
    result = {
        'valid': True,
        'errors': [],
        'strength': 'weak'
    }
    
    if len(password) < min_length:
        result['valid'] = False
        result['errors'].append(f'Password must be at least {min_length} characters long')
    
    if not re.search(r'[A-Z]', password):
        result['errors'].append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        result['errors'].append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        result['errors'].append('Password must contain at least one number')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['errors'].append('Password must contain at least one special character')
    
    if result['errors']:
        result['valid'] = False
    else:
        # Determine strength
        if len(password) >= 12 and len(result['errors']) == 0:
            result['strength'] = 'strong'
        elif len(password) >= 8:
            result['strength'] = 'medium'
    
    return result


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate that required fields are present and not empty.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Dictionary with validation result and missing fields
    """
    result = {
        'valid': True,
        'missing_fields': [],
        'empty_fields': []
    }
    
    for field in required_fields:
        if field not in data:
            result['missing_fields'].append(field)
            result['valid'] = False
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            result['empty_fields'].append(field)
            result['valid'] = False
    
    return result


def validate_string_length(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> bool:
    """
    Validate string length constraints.
    
    Args:
        value: String to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, str):
        return False
    
    if min_length is not None and len(value) < min_length:
        return False
    
    if max_length is not None and len(value) > max_length:
        return False
    
    return True


def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                          max_value: Optional[Union[int, float]] = None) -> bool:
    """
    Validate numeric value is within range.
    
    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False
    
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True


def validate_slug(slug: str) -> bool:
    """
    Validate slug format (alphanumeric, hyphens, underscores only).
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if valid slug format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, slug))


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string, re.IGNORECASE))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    return sanitized


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Basic JSON schema validation.
    
    Args:
        data: Data to validate
        schema: Schema definition
        
    Returns:
        Validation result with errors
    """
    result = {
        'valid': True,
        'errors': []
    }
    
    for field, rules in schema.items():
        if 'required' in rules and rules['required'] and field not in data:
            result['errors'].append(f'Field "{field}" is required')
            result['valid'] = False
            continue
        
        if field in data:
            value = data[field]
            
            # Type validation
            if 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'string' and not isinstance(value, str):
                    result['errors'].append(f'Field "{field}" must be a string')
                    result['valid'] = False
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    result['errors'].append(f'Field "{field}" must be a number')
                    result['valid'] = False
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    result['errors'].append(f'Field "{field}" must be a boolean')
                    result['valid'] = False
            
            # String length validation
            if isinstance(value, str) and 'min_length' in rules:
                if len(value) < rules['min_length']:
                    result['errors'].append(f'Field "{field}" must be at least {rules["min_length"]} characters')
                    result['valid'] = False
            
            if isinstance(value, str) and 'max_length' in rules:
                if len(value) > rules['max_length']:
                    result['errors'].append(f'Field "{field}" must be at most {rules["max_length"]} characters')
                    result['valid'] = False
    
    return result