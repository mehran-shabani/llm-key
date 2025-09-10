from django.db import models
from django.contrib.auth import get_user_model
from workspaces.models import Workspace

User = get_user_model()


class WorkspaceChat(models.Model):
    """Chat messages within workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    workspace_id = models.IntegerField()  # Not using ForeignKey to match original schema
    prompt = models.TextField()
    response = models.TextField()
    include = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workspace_chats')
    thread_id = models.IntegerField(null=True, blank=True)  # No relation to prevent migration issues
    api_session_id = models.CharField(max_length=255, null=True, blank=True)  # For API partitioning
    feedback_score = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_chats'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace_id']),
            models.Index(fields=['user']),
            models.Index(fields=['thread_id']),
            models.Index(fields=['api_session_id']),
        ]
    
    def __str__(self):
        return f"Chat {self.id} - {self.prompt[:50]}..."


class WelcomeMessage(models.Model):
    """Welcome messages for users."""
    
    id = models.BigAutoField(primary_key=True)
    user = models.CharField(max_length=255)
    response = models.TextField()
    order_index = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'welcome_messages'
        ordering = ['order_index', 'id']