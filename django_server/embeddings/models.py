from django.db import models
from django.contrib.auth import get_user_model
from workspaces.models import Workspace
import uuid

User = get_user_model()


class EmbedConfig(models.Model):
    """Configuration for embedded chat widgets."""
    
    CHAT_MODE_CHOICES = [
        ('query', 'Query'),
        ('chat', 'Chat'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    enabled = models.BooleanField(default=False)
    chat_mode = models.CharField(max_length=20, choices=CHAT_MODE_CHOICES, default='query')
    allowlist_domains = models.TextField(blank=True, null=True)
    allow_model_override = models.BooleanField(default=False)
    allow_temperature_override = models.BooleanField(default=False)
    allow_prompt_override = models.BooleanField(default=False)
    max_chats_per_day = models.IntegerField(null=True, blank=True)
    max_chats_per_session = models.IntegerField(null=True, blank=True)
    message_limit = models.IntegerField(default=20)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='embed_configs')
    created_by = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='embed_configs')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'embed_configs'
    
    def __str__(self):
        return f"Embed Config for {self.workspace.name}"


class EmbedChat(models.Model):
    """Chat messages from embedded widgets."""
    
    id = models.BigAutoField(primary_key=True)
    prompt = models.TextField()
    response = models.TextField()
    session_id = models.CharField(max_length=255)
    include = models.BooleanField(default=True)
    connection_information = models.JSONField(blank=True, null=True)
    embed_config = models.ForeignKey(EmbedConfig, on_delete=models.CASCADE, related_name='embed_chats')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='embed_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'embed_chats'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['embed_config']),
        ]
    
    def __str__(self):
        return f"Embed Chat {self.id} - Session {self.session_id}"