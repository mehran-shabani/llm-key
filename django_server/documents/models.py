from django.db import models
from workspaces.models import Workspace
import uuid


class WorkspaceDocument(models.Model):
    """Documents associated with workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    doc_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    filename = models.CharField(max_length=255)
    docpath = models.CharField(max_length=500)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='documents')
    metadata = models.JSONField(blank=True, null=True)
    pinned = models.BooleanField(default=False)
    watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_documents'
        ordering = ['-pinned', '-created_at']
    
    def __str__(self):
        return f"{self.workspace.name} - {self.filename}"


class DocumentVector(models.Model):
    """Vector embeddings for documents."""
    
    id = models.BigAutoField(primary_key=True)
    doc_id = models.CharField(max_length=255)
    vector_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_vectors'
        indexes = [
            models.Index(fields=['doc_id']),
            models.Index(fields=['vector_id']),
        ]


class DocumentSyncQueue(models.Model):
    """Queue for syncing documents."""
    
    id = models.BigAutoField(primary_key=True)
    stale_after_ms = models.IntegerField(default=604800000)  # 7 days
    next_sync_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    workspace_doc = models.OneToOneField(
        WorkspaceDocument, 
        on_delete=models.CASCADE, 
        related_name='sync_queue'
    )
    
    class Meta:
        db_table = 'document_sync_queues'


class DocumentSyncExecution(models.Model):
    """Execution history for document syncs."""
    
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    queue = models.ForeignKey(DocumentSyncQueue, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    result = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_sync_executions'
        ordering = ['-created_at']