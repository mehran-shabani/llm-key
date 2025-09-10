from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


class Workspace(models.Model):
    """Main workspace model for organizing chats and documents."""
    
    CHAT_MODE_CHOICES = [
        ('chat', 'Chat'),
        ('query', 'Query'),
    ]
    
    VECTOR_SEARCH_MODE_CHOICES = [
        ('default', 'Default'),
        ('hybrid', 'Hybrid'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    vector_tag = models.CharField(max_length=255, blank=True, null=True)
    
    # LLM Configuration
    openai_temp = models.FloatField(blank=True, null=True)
    openai_history = models.IntegerField(default=20)
    openai_prompt = models.TextField(blank=True, null=True)
    similarity_threshold = models.FloatField(default=0.25)
    chat_provider = models.CharField(max_length=50, blank=True, null=True)
    chat_model = models.CharField(max_length=255, blank=True, null=True)
    top_n = models.IntegerField(default=4)
    chat_mode = models.CharField(max_length=20, choices=CHAT_MODE_CHOICES, default='chat')
    
    # Agent Configuration
    agent_provider = models.CharField(max_length=50, blank=True, null=True)
    agent_model = models.CharField(max_length=255, blank=True, null=True)
    
    # UI Configuration
    pfp_filename = models.CharField(max_length=255, blank=True, null=True)
    query_refusal_response = models.TextField(blank=True, null=True)
    
    # Search Configuration
    vector_search_mode = models.CharField(max_length=20, choices=VECTOR_SEARCH_MODE_CHOICES, default='default')
    
    # Users (many-to-many through WorkspaceUser)
    users = models.ManyToManyField(User, through='WorkspaceUser', related_name='workspaces')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspaces'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WorkspaceUser(models.Model):
    """Many-to-many relationship between workspaces and users."""
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_users'
        unique_together = ['user', 'workspace']


class WorkspaceThread(models.Model):
    """Thread for organizing conversations within a workspace."""
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_threads'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workspace.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WorkspaceSuggestedMessage(models.Model):
    """Suggested messages for workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='suggested_messages')
    heading = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_suggested_messages'
        indexes = [
            models.Index(fields=['workspace']),
        ]


class WorkspaceAgentInvocation(models.Model):
    """Agent invocations for workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    prompt = models.TextField()  # Contains agent invocation to parse + optional additional text
    closed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    thread_id = models.IntegerField(null=True, blank=True)  # No relation to prevent migration issues
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='agent_invocations')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workspace_agent_invocations'
        indexes = [
            models.Index(fields=['uuid']),
        ]


class SlashCommandPreset(models.Model):
    """Slash command presets for users."""
    
    id = models.BigAutoField(primary_key=True)
    command = models.CharField(max_length=255)
    prompt = models.TextField()
    description = models.TextField()
    uid = models.IntegerField(default=0)  # 0 is null user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='slash_command_presets')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'slash_command_presets'
        unique_together = ['uid', 'command']


class PromptHistory(models.Model):
    """History of prompts for workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='prompt_history')
    prompt = models.TextField()
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prompt_history'
        indexes = [
            models.Index(fields=['workspace']),
        ]
        ordering = ['-modified_at']


class WorkspaceParsedFile(models.Model):
    """Parsed files associated with workspaces."""
    
    id = models.BigAutoField(primary_key=True)
    filename = models.CharField(max_length=255, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='parsed_files')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='parsed_files')
    thread = models.ForeignKey(WorkspaceThread, on_delete=models.CASCADE, null=True, blank=True, related_name='parsed_files')
    metadata = models.JSONField(blank=True, null=True)
    token_count_estimate = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workspace_parsed_files'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
        ]