# Feature: Multi-turn Conversations
# Description: Persistent conversation history with context management
# Library: Django, Django ORM

# 1. models.py - Chat history model
from django.db import models
from django.contrib.auth.models import User
import json

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkspaceChat(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    prompt = models.TextField()
    response = models.JSONField()  # Stores response text, sources, type
    thread_id = models.CharField(max_length=100, null=True, blank=True)
    include_in_context = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

# 2. views.py - Chat handler with context
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def post(self, request, workspace_slug):
        try:
            workspace = Workspace.objects.get(slug=workspace_slug)
            data = json.loads(request.body)
            message = data.get('message', '')
            thread_id = data.get('thread_id')
            
            # 3. Get recent chat history for context (last 20 messages)
            recent_chats = WorkspaceChat.objects.filter(
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None,
                thread_id=thread_id,
                include_in_context=True
            ).order_by('-created_at')[:20]
            
            # 4. Build conversation context
            conversation_history = []
            for chat in reversed(recent_chats):  # Reverse to get chronological order
                conversation_history.extend([
                    {"role": "user", "content": chat.prompt},
                    {"role": "assistant", "content": chat.response.get('text', '')}
                ])
            
            # 5. Add current message to context
            conversation_history.append({"role": "user", "content": message})
            
            # 6. Generate response (simplified LLM call)
            response_text = self.generate_response(conversation_history)
            
            # 7. Save chat to database
            chat = WorkspaceChat.objects.create(
                workspace=workspace,
                user=request.user if request.user.is_authenticated else None,
                prompt=message,
                response={'text': response_text, 'sources': [], 'type': 'chat'},
                thread_id=thread_id
            )
            
            return JsonResponse({
                'response': response_text,
                'chat_id': chat.id,
                'context_length': len(conversation_history)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def generate_response(self, conversation_history):
        # Simplified response generation based on context
        if len(conversation_history) > 2:
            return f"Based on our conversation history ({len(conversation_history)} messages), here's my response..."
        else:
            return "This is my first response in our conversation."

# 3. urls.py
from django.urls import path
from .views import ChatView

urlpatterns = [
    path('workspace/<str:workspace_slug>/chat/', ChatView.as_view()),
]