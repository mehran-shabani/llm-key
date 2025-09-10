from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Workspace, WorkspaceDocument, ApiKey, SystemSettings, Invite,
    RecoveryCode, PasswordResetToken, DocumentVector, WelcomeMessage,
    WorkspaceThread, WorkspaceSuggestedMessage, WorkspaceChat,
    WorkspaceAgentInvocation, WorkspaceUser, CacheData, EmbedConfig,
    EmbedChat, EventLog, SlashCommandPreset, DocumentSyncQueue,
    DocumentSyncExecution, BrowserExtensionApiKey, TemporaryAuthToken,
    SystemPromptVariable, PromptHistory, DesktopMobileDevice, WorkspaceParsedFile
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ('username', 'email', 'role', 'suspended', 'created_at')
    list_filter = ('role', 'suspended', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'suspended', 'pfp_filename', 'daily_message_limit', 'bio')}),
    )


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    """Admin for Workspace model"""
    list_display = ('name', 'slug', 'created_at', 'last_updated_at')
    list_filter = ('created_at', 'chat_mode', 'vector_search_mode')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(WorkspaceDocument)
class WorkspaceDocumentAdmin(admin.ModelAdmin):
    """Admin for WorkspaceDocument model"""
    list_display = ('filename', 'doc_id', 'workspace', 'pinned', 'watched', 'created_at')
    list_filter = ('pinned', 'watched', 'created_at', 'workspace')
    search_fields = ('filename', 'doc_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    """Admin for ApiKey model"""
    list_display = ('secret', 'created_by', 'created_at', 'last_updated_at')
    list_filter = ('created_at',)
    search_fields = ('secret',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin for SystemSettings model"""
    list_display = ('label', 'value', 'created_at', 'last_updated_at')
    list_filter = ('created_at',)
    search_fields = ('label',)
    ordering = ('label',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    """Admin for Invite model"""
    list_display = ('code', 'status', 'created_by', 'claimed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('code',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(WorkspaceThread)
class WorkspaceThreadAdmin(admin.ModelAdmin):
    """Admin for WorkspaceThread model"""
    list_display = ('name', 'slug', 'workspace', 'user', 'created_at')
    list_filter = ('created_at', 'workspace')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(WorkspaceChat)
class WorkspaceChatAdmin(admin.ModelAdmin):
    """Admin for WorkspaceChat model"""
    list_display = ('workspace', 'user', 'thread_id', 'include', 'created_at')
    list_filter = ('include', 'created_at', 'workspace')
    search_fields = ('prompt', 'response')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_updated_at')


@admin.register(EmbedConfig)
class EmbedConfigAdmin(admin.ModelAdmin):
    """Admin for EmbedConfig model"""
    list_display = ('uuid', 'enabled', 'workspace', 'created_by', 'created_at')
    list_filter = ('enabled', 'chat_mode', 'created_at')
    search_fields = ('uuid',)
    ordering = ('-created_at',)


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    """Admin for EventLog model"""
    list_display = ('event', 'user_id', 'occurred_at')
    list_filter = ('event', 'occurred_at')
    search_fields = ('event', 'metadata')
    ordering = ('-occurred_at',)
    readonly_fields = ('occurred_at',)


@admin.register(SystemPromptVariable)
class SystemPromptVariableAdmin(admin.ModelAdmin):
    """Admin for SystemPromptVariable model"""
    list_display = ('key', 'type', 'user', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('key', 'description')
    ordering = ('key',)
    readonly_fields = ('created_at', 'updated_at')


# Register other models with basic admin
admin.site.register(RecoveryCode)
admin.site.register(PasswordResetToken)
admin.site.register(DocumentVector)
admin.site.register(WelcomeMessage)
admin.site.register(WorkspaceSuggestedMessage)
admin.site.register(WorkspaceAgentInvocation)
admin.site.register(WorkspaceUser)
admin.site.register(CacheData)
admin.site.register(EmbedChat)
admin.site.register(SlashCommandPreset)
admin.site.register(DocumentSyncQueue)
admin.site.register(DocumentSyncExecution)
admin.site.register(BrowserExtensionApiKey)
admin.site.register(TemporaryAuthToken)
admin.site.register(PromptHistory)
admin.site.register(DesktopMobileDevice)
admin.site.register(WorkspaceParsedFile)