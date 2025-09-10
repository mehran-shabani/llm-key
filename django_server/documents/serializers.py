from rest_framework import serializers
from .models import WorkspaceDocument, DocumentVector, DocumentSyncQueue, DocumentSyncExecution


class WorkspaceDocumentSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceDocument model."""
    
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    sync_status = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkspaceDocument
        fields = [
            'id', 'doc_id', 'filename', 'docpath', 'workspace', 'workspace_name',
            'metadata', 'pinned', 'watched', 'sync_status', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'doc_id', 'created_at', 'last_updated_at']
    
    def get_sync_status(self, obj):
        """Get sync status if document is in sync queue."""
        try:
            sync_queue = obj.sync_queue
            last_run = sync_queue.runs.first()
            return {
                'next_sync_at': sync_queue.next_sync_at,
                'last_synced_at': sync_queue.last_synced_at,
                'last_status': last_run.status if last_run else None
            }
        except DocumentSyncQueue.DoesNotExist:
            return None


class DocumentVectorSerializer(serializers.ModelSerializer):
    """Serializer for DocumentVector model."""
    
    class Meta:
        model = DocumentVector
        fields = ['id', 'doc_id', 'vector_id', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class DocumentSyncQueueSerializer(serializers.ModelSerializer):
    """Serializer for DocumentSyncQueue model."""
    
    workspace_doc_name = serializers.CharField(source='workspace_doc.filename', read_only=True)
    last_run_status = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentSyncQueue
        fields = [
            'id', 'stale_after_ms', 'next_sync_at', 'workspace_doc', 'workspace_doc_name',
            'last_run_status', 'created_at', 'last_synced_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_synced_at']
    
    def get_last_run_status(self, obj):
        """Get status of last sync execution."""
        last_run = obj.runs.first()
        return last_run.status if last_run else None


class DocumentSyncExecutionSerializer(serializers.ModelSerializer):
    """Serializer for DocumentSyncExecution model."""
    
    class Meta:
        model = DocumentSyncExecution
        fields = ['id', 'queue', 'status', 'result', 'created_at']
        read_only_fields = ['id', 'created_at']


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload."""
    
    file = serializers.FileField(required=True)
    workspace_id = serializers.IntegerField(required=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (3GB limit)
        max_size = 3 * 1024 * 1024 * 1024  # 3GB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(f"File size exceeds maximum of 3GB")
        
        # Check file extension
        allowed_extensions = [
            '.txt', '.pdf', '.doc', '.docx', '.md', '.html', '.csv',
            '.json', '.xml', '.rtf', '.odt', '.xls', '.xlsx'
        ]
        
        import os
        _, ext = os.path.splitext(value.name)
        if ext.lower() not in allowed_extensions:
            raise serializers.ValidationError(f"File type {ext} is not supported")
        
        return value


class DocumentBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk document actions."""
    
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    action = serializers.ChoiceField(
        choices=['pin', 'unpin', 'watch', 'unwatch', 'delete'],
        required=True
    )