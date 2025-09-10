from django.db import models
from django.contrib.auth.models import User as DjangoUser


class ApiKey(models.Model):
    """API Keys for authentication"""
    id = models.AutoField(primary_key=True)
    secret = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_keys'


class User(models.Model):
    """Users table"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    pfp_filename = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, default='default')
    suspended = models.IntegerField(default=0)
    seen_recovery_codes = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    daily_message_limit = models.IntegerField(null=True, blank=True)
    bio = models.TextField(default='')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username or f"User {self.id}"


class Workspace(models.Model):
    """Workspaces table"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    vector_tag = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    open_ai_temp = models.FloatField(null=True, blank=True)
    open_ai_history = models.IntegerField(default=20)
    last_updated_at = models.DateTimeField(auto_now=True)
    open_ai_prompt = models.TextField(null=True, blank=True)
    similarity_threshold = models.FloatField(default=0.25)
    chat_provider = models.CharField(max_length=255, null=True, blank=True)
    chat_model = models.CharField(max_length=255, null=True, blank=True)
    top_n = models.IntegerField(default=4)
    chat_mode = models.CharField(max_length=50, default='chat')
    pfp_filename = models.CharField(max_length=255, null=True, blank=True)
    agent_provider = models.CharField(max_length=255, null=True, blank=True)
    agent_model = models.CharField(max_length=255, null=True, blank=True)
    query_refusal_response = models.TextField(null=True, blank=True)
    vector_search_mode = models.CharField(max_length=50, default='default')

    class Meta:
        db_table = 'workspaces'

    def __str__(self):
        return self.name


class WorkspaceUser(models.Model):
    """Workspace Users junction table"""
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    workspace_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    workspaces = models.ForeignKey(Workspace, on_delete=models.CASCADE, db_column='workspace_id')
    users = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')

    class Meta:
        db_table = 'workspace_users'


class WorkspaceChat(models.Model):
    """Workspace Chats table"""
    id = models.AutoField(primary_key=True)
    workspace_id = models.IntegerField()
    prompt = models.TextField()
    response = models.TextField()
    include = models.BooleanField(default=True)
    user_id = models.IntegerField(null=True, blank=True)
    thread_id = models.IntegerField(null=True, blank=True)
    api_session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    feedback_score = models.BooleanField(null=True, blank=True)
    users = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_column='user_id')

    class Meta:
        db_table = 'workspace_chats'


class Invite(models.Model):
    """Invites table"""
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')
    claimed_by = models.IntegerField(null=True, blank=True)
    workspace_ids = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invites'

    def __str__(self):
        return f"Invite {self.code}"


class SystemSetting(models.Model):
    """System Settings table"""
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255, unique=True)
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'

    def __str__(self):
        return f"{self.label}: {self.value}"


class EventLog(models.Model):
    """Event Logs table"""
    id = models.AutoField(primary_key=True)
    event = models.CharField(max_length=255)
    metadata = models.TextField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_logs'
        indexes = [
            models.Index(fields=['event']),
        ]

    def __str__(self):
        return f"{self.event} - {self.occurred_at}"


class WorkspaceDocument(models.Model):
    """Workspace Documents table"""
    id = models.AutoField(primary_key=True)
    doc_id = models.CharField(max_length=255, unique=True)
    filename = models.CharField(max_length=255)
    docpath = models.CharField(max_length=255)
    workspace_id = models.IntegerField()
    metadata = models.TextField(null=True, blank=True)
    pinned = models.BooleanField(default=False)
    watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, db_column='workspace_id')

    class Meta:
        db_table = 'workspace_documents'

    def __str__(self):
        return self.filename


class DocumentVector(models.Model):
    """Document Vectors table"""
    id = models.AutoField(primary_key=True)
    doc_id = models.CharField(max_length=255)
    vector_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_vectors'