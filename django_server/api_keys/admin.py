from django.contrib import admin
from .models import APIKey, BrowserExtensionAPIKey, Invite


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['label', 'user', 'created_at', 'last_used_at']
    list_filter = ['created_at', 'last_used_at']
    search_fields = ['label', 'user__username', 'user__email']
    readonly_fields = ['key_hash', 'created_at', 'last_used_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # API keys should be created through the API
        return False


@admin.register(BrowserExtensionAPIKey)
class BrowserExtensionAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['label', 'user', 'created_at', 'last_used_at']
    list_filter = ['created_at', 'last_used_at']
    search_fields = ['label', 'user__username', 'user__email']
    readonly_fields = ['key_hash', 'created_at', 'last_used_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        # API keys should be created through the API
        return False


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'status', 'created_by', 'created_at', 'accepted_at']
    list_filter = ['status', 'role', 'created_at', 'accepted_at']
    search_fields = ['name', 'email', 'invite_code', 'created_by__username']
    readonly_fields = ['invite_code', 'created_at', 'accepted_at', 'accepted_by']
    filter_horizontal = ['workspace_ids']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Invite Information', {
            'fields': ('name', 'email', 'role', 'invite_code')
        }),
        ('Status', {
            'fields': ('status', 'accepted_by', 'accepted_at')
        }),
        ('Permissions', {
            'fields': ('workspace_ids',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
