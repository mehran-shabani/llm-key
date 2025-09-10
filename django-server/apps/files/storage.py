from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class ConfigurableFileSystemStorage(FileSystemStorage):
    """
    Django FileSystemStorage with configurable root path.
    Uses Django settings to determine the storage root directory.
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = getattr(settings, 'FILES_ROOT', '/tmp/files')
        super().__init__(location, base_url)


class DocumentStorage(FileSystemStorage):
    """
    Specialized storage for document files.
    Uses configurable root path for documents.
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents')
        super().__init__(location, base_url)


class AssetStorage(FileSystemStorage):
    """
    Specialized storage for asset files (logos, etc.).
    Uses configurable root path for assets.
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = getattr(settings, 'ASSETS_ROOT', '/tmp/assets')
        super().__init__(location, base_url)


class ProfilePictureStorage(FileSystemStorage):
    """
    Specialized storage for profile pictures.
    Uses configurable root path for profile pictures.
    """
    
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = getattr(settings, 'PFP_ROOT', '/tmp/assets/pfp')
        super().__init__(location, base_url)


def normalize_path(filepath=""):
    """
    Normalize file path by removing dangerous path components.
    Equivalent to the Node.js normalizePath function.
    """
    if not filepath:
        return ""
    
    # Normalize the path and remove dangerous components
    result = os.path.normpath(filepath.strip())
    result = result.replace("..", "").replace("./", "").replace(".\\", "")
    result = result.strip()
    
    # Check for invalid paths
    if result in ["..", ".", "/", "\\"]:
        raise ValueError("Invalid path")
    
    return result


def is_within(outer_path, inner_path):
    """
    Check if inner_path is within outer_path.
    Equivalent to the Node.js isWithin function.
    """
    if outer_path == inner_path:
        return False
    
    try:
        rel_path = os.path.relpath(inner_path, outer_path)
        return not rel_path.startswith("..") and rel_path != ".."
    except ValueError:
        return False


def ensure_directory_exists(path):
    """
    Ensure that a directory exists, creating it if necessary.
    """
    os.makedirs(path, exist_ok=True)
    return path


def get_storage_paths():
    """
    Get all configured storage paths from Django settings.
    """
    return {
        'documents': getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents'),
        'files': getattr(settings, 'FILES_ROOT', '/tmp/files'),
        'assets': getattr(settings, 'ASSETS_ROOT', '/tmp/assets'),
        'pfp': getattr(settings, 'PFP_ROOT', '/tmp/assets/pfp'),
        'vector_cache': getattr(settings, 'VECTOR_CACHE_ROOT', '/tmp/vector-cache'),
        'direct_uploads': getattr(settings, 'DIRECT_UPLOADS_ROOT', '/tmp/direct-uploads'),
    }


def create_storage_instance(storage_type='files'):
    """
    Create a storage instance based on the storage type.
    
    Args:
        storage_type (str): Type of storage ('files', 'documents', 'assets', 'pfp')
    
    Returns:
        FileSystemStorage: Configured storage instance
    """
    storage_classes = {
        'files': ConfigurableFileSystemStorage,
        'documents': DocumentStorage,
        'assets': AssetStorage,
        'pfp': ProfilePictureStorage,
    }
    
    storage_class = storage_classes.get(storage_type, ConfigurableFileSystemStorage)
    return storage_class()