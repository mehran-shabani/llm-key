from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import json
import uuid
from datetime import datetime

from .storage import (
    ConfigurableFileSystemStorage,
    DocumentStorage,
    AssetStorage,
    ProfilePictureStorage,
    normalize_path,
    is_within,
    ensure_directory_exists,
    get_storage_paths,
    create_storage_instance,
)


class FileUploadView(APIView):
    """Handle generic file uploads."""
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """Upload a file to the files storage."""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"success": False, "error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            storage = create_storage_instance('files')
            
            # Normalize filename
            filename = normalize_path(uploaded_file.name)
            
            # Save the file
            saved_filename = storage.save(filename, uploaded_file)
            
            return Response({
                "success": True,
                "error": None,
                "file": {
                    "name": saved_filename,
                    "url": storage.url(saved_filename),
                    "path": storage.path(saved_filename),
                    "size": uploaded_file.size,
                }
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssetUploadView(APIView):
    """Handle asset file uploads (logos, etc.)."""
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """Upload an asset file."""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"success": False, "error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            storage = create_storage_instance('assets')
            
            # Normalize filename
            filename = normalize_path(uploaded_file.name)
            
            # Save the file
            saved_filename = storage.save(filename, uploaded_file)
            
            return Response({
                "success": True,
                "error": None,
                "file": {
                    "name": saved_filename,
                    "url": storage.url(saved_filename),
                    "path": storage.path(saved_filename),
                    "size": uploaded_file.size,
                }
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfilePictureUploadView(APIView):
    """Handle profile picture uploads."""
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """Upload a profile picture."""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {"success": False, "error": "No file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            storage = create_storage_instance('pfp')
            
            # Generate unique filename for profile pictures
            file_extension = os.path.splitext(uploaded_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save the file
            saved_filename = storage.save(unique_filename, uploaded_file)
            
            return Response({
                "success": True,
                "error": None,
                "file": {
                    "name": saved_filename,
                    "url": storage.url(saved_filename),
                    "path": storage.path(saved_filename),
                    "size": uploaded_file.size,
                }
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileListView(APIView):
    """List files in storage."""
    
    def get(self, request):
        """List all files in the files storage."""
        try:
            storage = create_storage_instance('files')
            storage_paths = get_storage_paths()
            
            # Get list of files
            files = []
            if os.path.exists(storage_paths['files']):
                for root, dirs, filenames in os.walk(storage_paths['files']):
                    for filename in filenames:
                        rel_path = os.path.relpath(os.path.join(root, filename), storage_paths['files'])
                        files.append({
                            "name": filename,
                            "path": rel_path,
                            "url": storage.url(rel_path),
                            "size": os.path.getsize(os.path.join(root, filename)),
                        })
            
            return Response({
                "success": True,
                "files": files
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDetailView(APIView):
    """Get details of a specific file."""
    
    def get(self, request, filename):
        """Get details of a specific file."""
        try:
            storage = create_storage_instance('files')
            
            if not storage.exists(filename):
                return Response(
                    {"success": False, "error": "File not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            file_path = storage.path(filename)
            file_stats = os.stat(file_path)
            
            return Response({
                "success": True,
                "file": {
                    "name": filename,
                    "path": file_path,
                    "url": storage.url(filename),
                    "size": file_stats.st_size,
                    "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                }
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDeleteView(APIView):
    """Delete a file."""
    
    def delete(self, request, filename):
        """Delete a specific file."""
        try:
            storage = create_storage_instance('files')
            
            if not storage.exists(filename):
                return Response(
                    {"success": False, "error": "File not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            storage.delete(filename)
            
            return Response({
                "success": True,
                "message": "File deleted successfully"
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileMoveView(APIView):
    """Move files within storage."""
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Move files within the storage directory."""
        try:
            files_to_move = request.data.get('files', [])
            storage = create_storage_instance('files')
            
            moved_files = []
            failed_files = []
            
            for file_info in files_to_move:
                source = file_info.get('from')
                destination = file_info.get('to')
                
                if not source or not destination:
                    failed_files.append({
                        "from": source,
                        "to": destination,
                        "error": "Missing source or destination"
                    })
                    continue
                
                try:
                    # Normalize paths
                    source = normalize_path(source)
                    destination = normalize_path(destination)
                    
                    # Check if source exists
                    if not storage.exists(source):
                        failed_files.append({
                            "from": source,
                            "to": destination,
                            "error": "Source file not found"
                        })
                        continue
                    
                    # Check if destination already exists
                    if storage.exists(destination):
                        failed_files.append({
                            "from": source,
                            "to": destination,
                            "error": "Destination file already exists"
                        })
                        continue
                    
                    # Move the file
                    source_path = storage.path(source)
                    destination_path = storage.path(destination)
                    
                    # Ensure destination directory exists
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    
                    # Move the file
                    os.rename(source_path, destination_path)
                    moved_files.append({
                        "from": source,
                        "to": destination
                    })
                    
                except Exception as e:
                    failed_files.append({
                        "from": source,
                        "to": destination,
                        "error": str(e)
                    })
            
            return Response({
                "success": True,
                "moved_files": moved_files,
                "failed_files": failed_files,
                "message": f"Moved {len(moved_files)} files successfully"
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StorageInfoView(APIView):
    """Get storage information."""
    
    def get(self, request):
        """Get information about storage paths and usage."""
        try:
            storage_paths = get_storage_paths()
            storage_info = {}
            
            for storage_type, path in storage_paths.items():
                if os.path.exists(path):
                    total_size = 0
                    file_count = 0
                    
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except OSError:
                                pass
                    
                    storage_info[storage_type] = {
                        "path": path,
                        "exists": True,
                        "total_size": total_size,
                        "file_count": file_count,
                    }
                else:
                    storage_info[storage_type] = {
                        "path": path,
                        "exists": False,
                        "total_size": 0,
                        "file_count": 0,
                    }
            
            return Response({
                "success": True,
                "storage_info": storage_info
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )