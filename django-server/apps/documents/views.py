from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
import os
import json
import uuid
from datetime import datetime

from .serializers import (
    DocumentUploadSerializer,
    DocumentUploadLinkSerializer,
    DocumentRawTextSerializer,
    DocumentResponseSerializer,
    DocumentListSerializer,
    DocumentFolderSerializer,
    DocumentMetadataSchemaSerializer,
    DocumentAcceptedTypesSerializer,
    DocumentCreateFolderSerializer,
    DocumentRemoveFolderSerializer,
    DocumentMoveFilesSerializer,
)


class DocumentUploadView(APIView):
    """Handle document file uploads."""
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """Upload a new file to be parsed and prepared for embedding."""
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get file and workspace info
            uploaded_file = serializer.validated_data['file']
            add_to_workspaces = serializer.validated_data.get('addToWorkspaces', '')
            
            # Use Django's FileSystemStorage for file handling
            storage = FileSystemStorage(
                location=getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents')
            )
            
            # Save the file
            filename = storage.save(uploaded_file.name, uploaded_file)
            
            # Process the document (placeholder for actual processing logic)
            # This would integrate with the collector API
            documents = [{
                "location": f"custom-documents/{filename}",
                "name": filename,
                "url": f"file://{storage.path(filename)}",
                "title": uploaded_file.name,
                "docAuthor": "Unknown",
                "description": "Unknown",
                "docSource": "a text file uploaded by the user.",
                "chunkSource": uploaded_file.name,
                "published": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
                "wordCount": 0,  # Would be calculated during processing
                "token_count_estimate": 0,  # Would be calculated during processing
            }]
            
            # Handle workspace addition if specified
            if add_to_workspaces:
                # Placeholder for workspace integration
                pass
            
            return Response({
                "success": True,
                "error": None,
                "documents": documents
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentUploadFolderView(APIView):
    """Handle document file uploads to specific folders."""
    parser_classes = [MultiPartParser]
    
    def post(self, request, folderName):
        """Upload a new file to a specific folder."""
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uploaded_file = serializer.validated_data['file']
            add_to_workspaces = serializer.validated_data.get('addToWorkspaces', '')
            
            # Normalize folder name
            folder_name = folderName or "custom-documents"
            
            # Use Django's FileSystemStorage with folder path
            storage = FileSystemStorage(
                location=os.path.join(
                    getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents'),
                    folder_name
                )
            )
            
            # Ensure directory exists
            os.makedirs(storage.location, exist_ok=True)
            
            # Save the file
            filename = storage.save(uploaded_file.name, uploaded_file)
            
            # Process the document
            documents = [{
                "location": f"{folder_name}/{filename}",
                "name": filename,
                "url": f"file://{storage.path(filename)}",
                "title": uploaded_file.name,
                "docAuthor": "Unknown",
                "description": "Unknown",
                "docSource": "a text file uploaded by the user.",
                "chunkSource": uploaded_file.name,
                "published": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
                "wordCount": 0,
                "token_count_estimate": 0,
            }]
            
            if add_to_workspaces:
                # Placeholder for workspace integration
                pass
            
            return Response({
                "success": True,
                "error": None,
                "documents": documents
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentUploadLinkView(APIView):
    """Handle document uploads via URL links."""
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Upload a document by scraping a URL."""
        serializer = DocumentUploadLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            link = serializer.validated_data['link']
            add_to_workspaces = serializer.validated_data.get('addToWorkspaces', '')
            scraper_headers = serializer.validated_data.get('scraperHeaders', {})
            
            # Placeholder for link processing logic
            # This would integrate with the collector API for link scraping
            documents = [{
                "id": str(uuid.uuid4()),
                "url": f"file://{os.path.basename(link)}.html",
                "title": f"{os.path.basename(link)}.html",
                "docAuthor": "no author found",
                "description": "No description found.",
                "docSource": "URL link uploaded by the user.",
                "chunkSource": f"{link}.html",
                "published": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
                "wordCount": 0,
                "pageContent": "Scraped content would go here...",
                "token_count_estimate": 0,
                "location": f"custom-documents/url-{os.path.basename(link)}-{str(uuid.uuid4())}.json"
            }]
            
            if add_to_workspaces:
                # Placeholder for workspace integration
                pass
            
            return Response({
                "success": True,
                "error": None,
                "documents": documents
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentRawTextView(APIView):
    """Handle raw text document uploads."""
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Upload a document by providing raw text content."""
        serializer = DocumentRawTextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            text_content = serializer.validated_data['textContent']
            add_to_workspaces = serializer.validated_data.get('addToWorkspaces', '')
            metadata = serializer.validated_data.get('metadata', {})
            
            # Validate required metadata
            required_metadata = ["title"]
            if not all(key in metadata and metadata[key] for key in required_metadata):
                return Response(
                    {
                        "success": False,
                        "error": f"You are missing required metadata key:value pairs in your request. Required metadata key:values are {', '.join(f\"'{v}'\" for v in required_metadata)}"
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            if not text_content or len(text_content) == 0:
                return Response(
                    {
                        "success": False,
                        "error": "The 'textContent' key cannot have an empty value."
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
            
            # Process raw text
            documents = [{
                "id": str(uuid.uuid4()),
                "url": f"file://{metadata.get('title', 'raw-document')}.txt",
                "title": metadata.get('title', 'raw-document'),
                "docAuthor": metadata.get('docAuthor', 'no author found'),
                "description": metadata.get('description', 'No description found.'),
                "docSource": metadata.get('docSource', 'Raw text uploaded by the user'),
                "chunkSource": metadata.get('chunkSource', 'no chunk source specified'),
                "published": datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p"),
                "wordCount": len(text_content.split()),
                "pageContent": text_content,
                "token_count_estimate": len(text_content.split()) * 1.3,  # Rough estimate
                "location": f"custom-documents/raw-{metadata.get('title', 'doc')}-{str(uuid.uuid4())}.json"
            }]
            
            if add_to_workspaces:
                # Placeholder for workspace integration
                pass
            
            return Response({
                "success": True,
                "error": None,
                "documents": documents
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentListView(APIView):
    """List all locally-stored documents."""
    
    def get(self, request):
        """Get list of all documents."""
        try:
            # Placeholder for document listing logic
            # This would integrate with the file system to list documents
            local_files = {
                "name": "documents",
                "type": "folder",
                "items": []
            }
            
            return Response({"localFiles": local_files})
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentFolderView(APIView):
    """Get documents from a specific folder."""
    
    def get(self, request, folderName):
        """Get all documents stored in a specific folder."""
        try:
            # Placeholder for folder-specific document listing
            result = {
                "folder": folderName,
                "documents": []
            }
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentAcceptedTypesView(APIView):
    """Get accepted file types for upload."""
    
    def get(self, request):
        """Check available filetypes and MIMEs that can be uploaded."""
        try:
            # Placeholder for accepted file types
            types = {
                "application/mbox": [".mbox"],
                "application/pdf": [".pdf"],
                "application/vnd.oasis.opendocument.text": [".odt"],
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                "text/plain": [".txt", ".md"]
            }
            
            return Response({"types": types})
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentMetadataSchemaView(APIView):
    """Get metadata schema for raw text uploads."""
    
    def get(self, request):
        """Get the known available metadata schema."""
        try:
            schema = {
                "url": "string | nullable",
                "title": "string",
                "docAuthor": "string | nullable",
                "description": "string | nullable",
                "docSource": "string | nullable",
                "chunkSource": "string | nullable",
                "published": "epoch timestamp in ms | nullable",
            }
            
            return Response({"schema": schema})
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentDetailView(APIView):
    """Get a single document by name."""
    
    def get(self, request, docName):
        """Get a single document by its unique name."""
        try:
            # Placeholder for single document retrieval
            document = None  # Would be retrieved from file system
            
            if not document:
                return Response(
                    {"error": "Document not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({"document": document})
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentCreateFolderView(APIView):
    """Create a new folder in documents storage."""
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Create a new folder inside the documents storage directory."""
        serializer = DocumentCreateFolderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            name = serializer.validated_data['name']
            storage_path = os.path.join(
                getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents'),
                name
            )
            
            if os.path.exists(storage_path):
                return Response(
                    {
                        "success": False,
                        "message": "Folder by that name already exists"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            os.makedirs(storage_path, exist_ok=True)
            return Response({"success": True, "message": None})
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Failed to create folder: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentRemoveFolderView(APIView):
    """Remove a folder and all its contents."""
    parser_classes = [JSONParser]
    
    def delete(self, request):
        """Remove a folder and all its contents from the documents storage directory."""
        serializer = DocumentRemoveFolderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            name = serializer.validated_data['name']
            storage_path = os.path.join(
                getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents'),
                name
            )
            
            if os.path.exists(storage_path):
                import shutil
                shutil.rmtree(storage_path)
            
            return Response({
                "success": True,
                "message": "Folder removed successfully"
            })
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Failed to remove folder: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentMoveFilesView(APIView):
    """Move files within the documents storage directory."""
    parser_classes = [JSONParser]
    
    def post(self, request):
        """Move files within the documents storage directory."""
        serializer = DocumentMoveFilesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            files = serializer.validated_data['files']
            documents_root = getattr(settings, 'DOCUMENTS_ROOT', '/tmp/documents')
            
            # Placeholder for file moving logic
            # This would check for embedded files and move only non-embedded ones
            
            return Response({
                "success": True,
                "message": None
            })
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Failed to move files: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )