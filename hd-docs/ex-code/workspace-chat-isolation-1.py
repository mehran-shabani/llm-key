# Feature: Workspace-based Chat Isolation
# Description: Each workspace functions as isolated chat environment
# Library: Django, Django ORM

# 1. models.py - Workspace and user access models
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    chat_provider = models.CharField(max_length=50, default='openai')
    chat_model = models.CharField(max_length=100, default='gpt-3.5-turbo')
    system_prompt = models.TextField(default='You are a helpful assistant.')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class WorkspaceUser(models.Model):
    ROLES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default='member')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('workspace', 'user')

class WorkspaceChat(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    prompt = models.TextField()
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

# 2. middleware.py - Workspace access control
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

class WorkspaceAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if this is a workspace-specific endpoint
        if '/workspace/' in request.path:
            workspace_slug = self.extract_workspace_slug(request.path)
            if workspace_slug:
                request.workspace = self.validate_workspace_access(request, workspace_slug)
                if not request.workspace:
                    return JsonResponse({'error': 'Workspace not found or access denied'}, status=404)
        
        response = self.get_response(request)
        return response
    
    def extract_workspace_slug(self, path):
        # Extract workspace slug from URL pattern /workspace/{slug}/...
        parts = path.split('/')
        try:
            workspace_index = parts.index('workspace')
            return parts[workspace_index + 1]
        except (ValueError, IndexError):
            return None
    
    def validate_workspace_access(self, request, slug):
        try:
            workspace = Workspace.objects.get(slug=slug)
            
            # Check if user has access to this workspace
            if request.user.is_authenticated:
                workspace_user = WorkspaceUser.objects.filter(
                    workspace=workspace, 
                    user=request.user
                ).first()
                if workspace_user or request.user.is_superuser:
                    return workspace
            
            return None
        except Workspace.DoesNotExist:
            return None

# 3. views.py - Isolated workspace chat
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class WorkspaceChatView(View):
    def post(self, request, workspace_slug):
        try:
            # Workspace is already validated by middleware
            workspace = request.workspace
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Get chat history isolated to this workspace
            workspace_chats = WorkspaceChat.objects.filter(
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None
            ).order_by('-created_at')[:10]
            
            # Build isolated context for this workspace only
            context = f"Workspace: {workspace.name}\nSystem: {workspace.system_prompt}\n"
            for chat in reversed(workspace_chats):
                context += f"User: {chat.prompt}\nAssistant: {chat.response.get('text', '')}\n"
            
            # Generate response using workspace-specific settings
            response_text = self.generate_workspace_response(workspace, message, context)
            
            # Save to workspace-isolated chat history
            chat = WorkspaceChat.objects.create(
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None,
                prompt=message,
                response={'text': response_text, 'model': workspace.chat_model}
            )
            
            return JsonResponse({
                'response': response_text,
                'workspace': workspace.name,
                'model': workspace.chat_model,
                'chat_count': WorkspaceChat.objects.filter(workspace=workspace).count()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_workspace_response(self, workspace, message, context):
        # Simulate workspace-specific response generation
        return f"[{workspace.chat_model}] In workspace '{workspace.name}': {message[:50]}..."

# 4. urls.py
from django.urls import path
from .views import WorkspaceChatView

urlpatterns = [
    path('workspace/<str:workspace_slug>/chat/', WorkspaceChatView.as_view()),
]