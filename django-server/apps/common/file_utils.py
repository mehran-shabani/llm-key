"""
File utilities for Django applications.
Contains file handling, validation, and management functions.
"""

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile


def normalize_path(filepath: str) -> str:
    """
    Normalize file path and remove dangerous path components.
    
    Args:
        filepath: File path to normalize
        
    Returns:
        Normalized file path
        
    Raises:
        ValueError: If path is invalid
    """
    if not filepath:
        raise ValueError("Invalid path.")
    
    # Normalize path and remove dangerous components
    result = os.path.normpath(filepath.strip()).replace('\\', '/')
    result = result.lstrip('./')
    
    # Check for dangerous paths
    if result in ('..', '.', '/') or result.startswith('../'):
        raise ValueError("Invalid path.")
    
    return result


def is_within_path(outer_path: str, inner_path: str) -> bool:
    """
    Check if inner path is within outer path (security check).
    
    Args:
        outer_path: The outer path
        inner_path: The inner path to check
        
    Returns:
        True if inner path is within outer path, False otherwise
    """
    if outer_path == inner_path:
        return False
    
    try:
        outer = Path(outer_path).resolve()
        inner = Path(inner_path).resolve()
        return str(inner).startswith(str(outer))
    except (OSError, ValueError):
        return False


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    
    return sanitized


def get_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        File hash as hexadecimal string
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (OSError, IOError):
        return ""


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return 0


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including dot)
    """
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Check if file type is allowed.
    
    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (with or without dots)
        
    Returns:
        True if file type is allowed, False otherwise
    """
    ext = get_file_extension(filename)
    
    # Normalize extensions (add dots if missing)
    normalized_allowed = []
    for allowed_ext in allowed_extensions:
        if not allowed_ext.startswith('.'):
            allowed_ext = '.' + allowed_ext
        normalized_allowed.append(allowed_ext.lower())
    
    return ext in normalized_allowed


def create_unique_filename(filename: str, directory: str = "") -> str:
    """
    Create unique filename by adding UUID if file exists.
    
    Args:
        filename: Original filename
        directory: Directory to check for existing files
        
    Returns:
        Unique filename
    """
    name, ext = os.path.splitext(filename)
    
    if directory:
        full_path = os.path.join(directory, filename)
    else:
        full_path = filename
    
    if not os.path.exists(full_path):
        return filename
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    return f"{name}_{unique_id}{ext}"


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to directory
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
    except (OSError, IOError) as e:
        raise ValueError(f"Cannot create directory {directory_path}: {e}")


def get_storage_paths() -> Dict[str, str]:
    """
    Get storage paths for different file types.
    
    Returns:
        Dictionary with storage paths
    """
    base_storage = getattr(settings, 'STORAGE_DIR', '/tmp/storage')
    
    return {
        'documents': os.path.join(base_storage, 'documents'),
        'direct_uploads': os.path.join(base_storage, 'direct-uploads'),
        'vector_cache': os.path.join(base_storage, 'vector-cache'),
        'temp': os.path.join(base_storage, 'temp')
    }


def get_file_mime_type(filename: str) -> str:
    """
    Get MIME type for a file based on extension.
    
    Args:
        filename: Filename
        
    Returns:
        MIME type string
    """
    import mimetypes
    
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if file size is valid, False otherwise
    """
    return file_size <= max_size


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        return {
            'name': filename,
            'path': file_path,
            'size': stat.st_size,
            'extension': get_file_extension(filename),
            'mime_type': get_file_mime_type(filename),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'hash': get_file_hash(file_path),
            'exists': True
        }
    except (OSError, IOError):
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': 0,
            'extension': get_file_extension(file_path),
            'mime_type': 'application/octet-stream',
            'created': 0,
            'modified': 0,
            'hash': '',
            'exists': False
        }


def cleanup_temp_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up temporary files older than specified age.
    
    Args:
        directory: Directory to clean up
        max_age_hours: Maximum age of files in hours
        
    Returns:
        Number of files cleaned up
    """
    import time
    
    if not os.path.exists(directory):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    cleaned_count = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    cleaned_count += 1
    except (OSError, IOError):
        pass
    
    return cleaned_count


def get_directory_size(directory: str) -> int:
    """
    Calculate total size of directory.
    
    Args:
        directory: Directory path
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    continue
    except (OSError, IOError):
        pass
    
    return total_size