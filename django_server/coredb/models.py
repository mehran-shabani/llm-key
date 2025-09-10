from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom user model based on Prisma users table"""
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    pfp_filename = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=50, default='default')
    suspended = models.IntegerField(default=0)
    seen_recovery_codes = models.BooleanField(default=False)
    daily_message_limit = models.IntegerField(null=True, blank=True)
    bio = models.TextField(default='')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class Workspace(models.Model):
    """Workspace model based on Prisma workspaces table"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    vector_tag = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    openai_temp = models.FloatField(null=True, blank=True)
    openai_history = models.IntegerField(default=20)
    last_updated_at = models.DateTimeField(default=timezone.now)
    openai_prompt = models.TextField(null=True, blank=True)
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
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WorkspaceDocument(models.Model):
    """Workspace document model based on Prisma workspace_documents table"""
    doc_id = models.CharField(max_length=255, unique=True)
    filename = models.CharField(max_length=255)
    docpath = models.CharField(max_length=500)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='documents')
    metadata = models.TextField(null=True, blank=True)
    pinned = models.BooleanField(default=False)
    watched = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_documents'
        indexes = [
            models.Index(fields=['doc_id']),
            models.Index(fields=['workspace']),
            models.Index(fields=['filename']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename} ({self.doc_id})"


class ApiKey(models.Model):
    """API key model based on Prisma api_keys table"""
    secret = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'api_keys'
        indexes = [
            models.Index(fields=['secret']),
            models.Index(fields=['created_by']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class SystemSettings(models.Model):
    """System settings model based on Prisma system_settings table"""
    label = models.CharField(max_length=255, unique=True)
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'system_settings'
        indexes = [
            models.Index(fields=['label']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


class Invite(models.Model):
    """Invite model based on Prisma invites table"""
    code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    workspace_ids = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invites')
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'invites'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class RecoveryCode(models.Model):
    """Recovery code model based on Prisma recovery_codes table"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recovery_codes')
    code_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'recovery_codes'
        indexes = [
            models.Index(fields=['user']),
        ]


class PasswordResetToken(models.Model):
    """Password reset token model based on Prisma password_reset_tokens table"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'password_reset_tokens'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
        ]


class DocumentVector(models.Model):
    """Document vector model based on Prisma document_vectors table"""
    doc_id = models.CharField(max_length=255)
    vector_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'document_vectors'
        indexes = [
            models.Index(fields=['doc_id']),
            models.Index(fields=['vector_id']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class WelcomeMessage(models.Model):
    """Welcome message model based on Prisma welcome_messages table"""
    user = models.CharField(max_length=255)
    response = models.TextField()
    order_index = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'welcome_messages'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['order_index']),
        ]


class WorkspaceThread(models.Model):
    """Workspace thread model based on Prisma workspace_threads table"""
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='threads')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_threads'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.workspace.name})"


class WorkspaceSuggestedMessage(models.Model):
    """Workspace suggested message model based on Prisma workspace_suggested_messages table"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='suggested_messages')
    heading = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_suggested_messages'
        indexes = [
            models.Index(fields=['workspace']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class WorkspaceChat(models.Model):
    """Workspace chat model based on Prisma workspace_chats table"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='chats')
    prompt = models.TextField()
    response = models.TextField()
    include = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workspace_chats')
    thread_id = models.IntegerField(null=True, blank=True)  # No relation to prevent whole table migration
    api_session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)
    feedback_score = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'workspace_chats'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
            models.Index(fields=['thread_id']),
            models.Index(fields=['api_session_id']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class WorkspaceAgentInvocation(models.Model):
    """Workspace agent invocation model based on Prisma workspace_agent_invocations table"""
    uuid = models.CharField(max_length=255, unique=True)
    prompt = models.TextField()
    closed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workspace_agent_invocations')
    thread_id = models.IntegerField(null=True, blank=True)  # No relation to prevent whole table migration
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='agent_invocations')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_agent_invocations'
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class WorkspaceUser(models.Model):
    """Workspace user model based on Prisma workspace_users table"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_users')
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='workspace_users')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_users'
        unique_together = [['user', 'workspace']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['workspace']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class CacheData(models.Model):
    """Cache data model based on Prisma cache_data table"""
    name = models.CharField(max_length=255)
    data = models.TextField()
    belongs_to = models.CharField(max_length=255, null=True, blank=True)
    by_id = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cache_data'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['belongs_to']),
            models.Index(fields=['by_id']),
            models.Index(fields=['expires_at']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class EmbedConfig(models.Model):
    """Embed config model based on Prisma embed_configs table"""
    uuid = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(default=False)
    chat_mode = models.CharField(max_length=50, default='query')
    allowlist_domains = models.TextField(null=True, blank=True)
    allow_model_override = models.BooleanField(default=False)
    allow_temperature_override = models.BooleanField(default=False)
    allow_prompt_override = models.BooleanField(default=False)
    max_chats_per_day = models.IntegerField(null=True, blank=True)
    max_chats_per_session = models.IntegerField(null=True, blank=True)
    message_limit = models.IntegerField(default=20)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='embed_configs')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='embed_configs')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'embed_configs'
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['workspace']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"Embed Config {self.uuid}"


class EmbedChat(models.Model):
    """Embed chat model based on Prisma embed_chats table"""
    prompt = models.TextField()
    response = models.TextField()
    session_id = models.CharField(max_length=255)
    include = models.BooleanField(default=True)
    connection_information = models.TextField(null=True, blank=True)
    embed_config = models.ForeignKey(EmbedConfig, on_delete=models.CASCADE, related_name='embed_chats')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='embed_chats')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'embed_chats'
        indexes = [
            models.Index(fields=['embed_config']),
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
        ]


class EventLog(models.Model):
    """Event log model based on Prisma event_logs table"""
    event = models.CharField(max_length=255)
    metadata = models.TextField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'event_logs'
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['user_id']),
            models.Index(fields=['occurred_at']),
        ]


class SlashCommandPreset(models.Model):
    """Slash command preset model based on Prisma slash_command_presets table"""
    command = models.CharField(max_length=255)
    prompt = models.TextField()
    description = models.TextField()
    uid = models.IntegerField(default=0)  # 0 is null user
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='slash_command_presets')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'slash_command_presets'
        unique_together = [['uid', 'command']]
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['command']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class DocumentSyncQueue(models.Model):
    """Document sync queue model based on Prisma document_sync_queues table"""
    stale_after_ms = models.IntegerField(default=604800000)  # 7 days
    next_sync_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    last_synced_at = models.DateTimeField(default=timezone.now)
    workspace_doc = models.OneToOneField(WorkspaceDocument, on_delete=models.CASCADE, related_name='sync_queue')

    class Meta:
        db_table = 'document_sync_queues'
        indexes = [
            models.Index(fields=['next_sync_at']),
            models.Index(fields=['workspace_doc']),
        ]

    def save(self, *args, **kwargs):
        self.last_synced_at = timezone.now()
        super().save(*args, **kwargs)


class DocumentSyncExecution(models.Model):
    """Document sync execution model based on Prisma document_sync_executions table"""
    queue = models.ForeignKey(DocumentSyncQueue, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=50, default='unknown')
    result = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'document_sync_executions'
        indexes = [
            models.Index(fields=['queue']),
            models.Index(fields=['status']),
        ]


class BrowserExtensionApiKey(models.Model):
    """Browser extension API key model based on Prisma browser_extension_api_keys table"""
    key = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='browser_extension_api_keys')
    created_at = models.DateTimeField(default=timezone.now)
    last_updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'browser_extension_api_keys'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['key']),
        ]

    def save(self, *args, **kwargs):
        self.last_updated_at = timezone.now()
        super().save(*args, **kwargs)


class TemporaryAuthToken(models.Model):
    """Temporary auth token model based on Prisma temporary_auth_tokens table"""
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporary_auth_tokens')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'temporary_auth_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user']),
        ]


class SystemPromptVariable(models.Model):
    """System prompt variable model based on Prisma system_prompt_variables table"""
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50, default='system')  # system, user, dynamic
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='system_prompt_variables')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'system_prompt_variables'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['key']),
        ]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class PromptHistory(models.Model):
    """Prompt history model based on Prisma prompt_history table"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='prompt_history')
    prompt = models.TextField()
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='prompt_history')
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'prompt_history'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['modified_by']),
        ]


class DesktopMobileDevice(models.Model):
    """Desktop mobile device model based on Prisma desktop_mobile_devices table"""
    device_os = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    approved = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='desktop_mobile_devices')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'desktop_mobile_devices'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
        ]


class WorkspaceParsedFile(models.Model):
    """Workspace parsed file model based on Prisma workspace_parsed_files table"""
    filename = models.CharField(max_length=255, unique=True)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='parsed_files')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='workspace_parsed_files')
    thread = models.ForeignKey(WorkspaceThread, on_delete=models.CASCADE, null=True, blank=True, related_name='parsed_files')
    metadata = models.TextField(null=True, blank=True)
    token_count_estimate = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'workspace_parsed_files'
        indexes = [
            models.Index(fields=['workspace']),
            models.Index(fields=['user']),
            models.Index(fields=['filename']),
        ]