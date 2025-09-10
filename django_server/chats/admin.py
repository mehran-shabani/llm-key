from django.contrib import admin
from .models import WorkspaceChat, WelcomeMessage


@admin.register(WorkspaceChat)
class WorkspaceChatAdmin(admin.ModelAdmin):
    list_display = ['id', 'workspace', 'user', 'thread', 'feedback_score', 'created_at']
    list_filter = ['include', 'feedback_score', 'created_at']
    search_fields = ['prompt', 'response', 'user__username', 'workspace__name']
    readonly_fields = ['created_at', 'last_updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Chat Information', {
            'fields': ('workspace', 'user', 'thread', 'api_session_id')
        }),
        ('Content', {
            'fields': ('prompt', 'response', 'include')
        }),
        ('Feedback', {
            'fields': ('feedback_score',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('workspace', 'user', 'thread')


@admin.register(WelcomeMessage)
class WelcomeMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_index', 'created_at']
    list_filter = ['created_at']
    search_fields = ['response', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['user', 'order_index']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('user', 'response', 'order_index')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
