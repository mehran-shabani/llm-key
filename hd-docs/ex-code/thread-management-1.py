# Feature: Thread Management
# Description: Multiple conversation threads within workspaces
# Library: Django, Django ORM

# 1. models.py - Thread model with workspace relationship
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkspaceThread(models.Model):
    name = models.CharField(max_length=100, default='Thread')
    slug = models.SlugField()
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('workspace', 'slug')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def auto_rename_from_message(self, message):
        """Auto-rename thread based on first message"""
        if self.name == 'Thread' and not self.chats.exists():
            # Truncate message to create thread name
            new_name = message[:50].strip()
            if new_name:
                self.name = new_name
                self.save()
                return True
        return False

class WorkspaceChat(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    thread = models.ForeignKey(WorkspaceThread, on_delete=models.CASCADE, related_name='chats', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    prompt = models.TextField()
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

# 2. views.py - Thread management endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
import json

@method_decorator(csrf_exempt, name='dispatch')
class ThreadCreateView(View):
    def post(self, request, workspace_slug):
        try:
            workspace = get_object_or_404(Workspace, slug=workspace_slug)
            data = json.loads(request.body)
            
            thread = WorkspaceThread.objects.create(
                name=data.get('name', 'Thread'),
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None
            )
            
            return JsonResponse({
                'thread': {
                    'id': thread.id,
                    'name': thread.name,
                    'slug': thread.slug,
                    'created_at': thread.created_at.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ThreadListView(View):
    def get(self, request, workspace_slug):
        try:
            workspace = get_object_or_404(Workspace, slug=workspace_slug)
            
            # Get threads for this workspace and user
            threads = WorkspaceThread.objects.filter(
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None
            ).order_by('-updated_at')
            
            thread_list = []
            for thread in threads:
                # Get chat count and last message for each thread
                chat_count = thread.chats.count()
                last_chat = thread.chats.last()
                
                thread_list.append({
                    'id': thread.id,
                    'name': thread.name,
                    'slug': thread.slug,
                    'chat_count': chat_count,
                    'last_message': last_chat.prompt if last_chat else None,
                    'updated_at': thread.updated_at.isoformat()
                })
            
            return JsonResponse({'threads': thread_list})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ThreadChatView(View):
    def post(self, request, workspace_slug, thread_slug):
        try:
            workspace = get_object_or_404(Workspace, slug=workspace_slug)
            thread = get_object_or_404(WorkspaceThread, workspace=workspace, slug=thread_slug)
            
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Auto-rename thread based on first message
            renamed = thread.auto_rename_from_message(message)
            
            # Get thread-specific chat history
            thread_chats = WorkspaceChat.objects.filter(
                workspace=workspace,
                thread=thread,
                user=request.user if request.user.is_authenticated else None
            ).order_by('-created_at')[:10]
            
            # Generate response with thread context
            response_text = f"Thread '{thread.name}' response: {message[:30]}..."
            
            # Save chat to specific thread
            chat = WorkspaceChat.objects.create(
                workspace=workspace,
                thread=thread,
                user=request.user if request.user.is_authenticated else None,
                prompt=message,
                response={'text': response_text}
            )
            
            # Update thread timestamp
            thread.save()  # This updates updated_at
            
            result = {
                'response': response_text,
                'thread': {
                    'id': thread.id,
                    'name': thread.name,
                    'slug': thread.slug,
                    'chat_count': thread.chats.count()
                }
            }
            
            if renamed:
                result['thread_renamed'] = True
                result['new_thread_name'] = thread.name
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ThreadUpdateView(View):
    def patch(self, request, workspace_slug, thread_slug):
        try:
            workspace = get_object_or_404(Workspace, slug=workspace_slug)
            thread = get_object_or_404(WorkspaceThread, workspace=workspace, slug=thread_slug)
            
            data = json.loads(request.body)
            
            if 'name' in data:
                thread.name = data['name']
                thread.save()
            
            return JsonResponse({
                'thread': {
                    'id': thread.id,
                    'name': thread.name,
                    'slug': thread.slug,
                    'updated_at': thread.updated_at.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 3. urls.py
from django.urls import path
from .views import ThreadCreateView, ThreadListView, ThreadChatView, ThreadUpdateView

urlpatterns = [
    path('workspace/<str:workspace_slug>/thread/new/', ThreadCreateView.as_view()),
    path('workspace/<str:workspace_slug>/threads/', ThreadListView.as_view()),
    path('workspace/<str:workspace_slug>/thread/<str:thread_slug>/chat/', ThreadChatView.as_view()),
    path('workspace/<str:workspace_slug>/thread/<str:thread_slug>/update/', ThreadUpdateView.as_view()),
]