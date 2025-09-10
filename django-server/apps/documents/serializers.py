from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload requests."""
    file = serializers.FileField()
    addToWorkspaces = serializers.CharField(required=False, allow_blank=True)


class DocumentUploadLinkSerializer(serializers.Serializer):
    """Serializer for document upload via link requests."""
    link = serializers.URLField()
    addToWorkspaces = serializers.CharField(required=False, allow_blank=True)
    scraperHeaders = serializers.DictField(required=False, default=dict)


class DocumentRawTextSerializer(serializers.Serializer):
    """Serializer for raw text document upload requests."""
    textContent = serializers.CharField()
    addToWorkspaces = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.DictField(required=False, default=dict)


class DocumentResponseSerializer(serializers.Serializer):
    """Serializer for document response data."""
    success = serializers.BooleanField()
    error = serializers.CharField(allow_null=True)
    documents = serializers.ListField(child=serializers.DictField(), required=False)


class DocumentListSerializer(serializers.Serializer):
    """Serializer for document list responses."""
    localFiles = serializers.DictField()


class DocumentFolderSerializer(serializers.Serializer):
    """Serializer for folder-specific document responses."""
    folder = serializers.CharField()
    documents = serializers.ListField(child=serializers.DictField())


class DocumentMetadataSchemaSerializer(serializers.Serializer):
    """Serializer for metadata schema responses."""
    schema = serializers.DictField()


class DocumentAcceptedTypesSerializer(serializers.Serializer):
    """Serializer for accepted file types responses."""
    types = serializers.DictField()


class DocumentCreateFolderSerializer(serializers.Serializer):
    """Serializer for creating document folders."""
    name = serializers.CharField()


class DocumentRemoveFolderSerializer(serializers.Serializer):
    """Serializer for removing document folders."""
    name = serializers.CharField()


class DocumentMoveFilesSerializer(serializers.Serializer):
    """Serializer for moving document files."""
    files = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )