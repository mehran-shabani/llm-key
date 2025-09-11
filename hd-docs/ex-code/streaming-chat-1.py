# Feature: Streaming Chat Interface
# Description: Real-time streaming chat with Server-Sent Events (SSE)
# Library: Django, Django Channels

# 1. views.py - Streaming chat endpoint
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
import time

@method_decorator(csrf_exempt, name='dispatch')
class StreamChatView(View):
    def post(self, request, workspace_slug):
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({'error': 'Message is empty'}, status=400)
            
            # Set SSE headers
            def event_stream():
                yield f"data: {json.dumps({'type': 'start', 'id': str(uuid.uuid4())})}\n\n"
                
                # Simulate streaming LLM response
                response_text = "This is a streaming response from the AI assistant."
                for i, word in enumerate(response_text.split()):
                    chunk_data = {
                        'type': 'textResponseChunk',
                        'textResponse': word + ' ',
                        'close': i == len(response_text.split()) - 1
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    time.sleep(0.1)  # Simulate processing delay
                
                yield f"data: {json.dumps({'type': 'end', 'close': True})}\n\n"
            
            response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['Connection'] = 'keep-alive'
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 2. urls.py
from django.urls import path
from .views import StreamChatView

urlpatterns = [
    path('workspace/<str:workspace_slug>/stream-chat/', StreamChatView.as_view()),
]