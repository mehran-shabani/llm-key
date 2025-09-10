from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json
import uuid as uuid_lib

from .models import WorkspaceChat, WelcomeMessage
from .serializers import (
    WorkspaceChatSerializer, ChatStreamSerializer, ChatHistorySerializer,
    ChatFeedbackSerializer, WelcomeMessageSerializer, ChatExportSerializer,
    ChatSearchSerializer
)
from workspaces.models import Workspace, WorkspaceThread
from system_settings.models import EventLog, Telemetry
from authentication.models import User


class WorkspaceChatViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkspaceChat management."""
    queryset = WorkspaceChat.objects.all()
    serializer_class = WorkspaceChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter chats based on user access."""
        user = self.request.user
        
        if user.role == 'admin':
            queryset = self.queryset
        else:
            # Filter by user's chats
            queryset = self.queryset.filter(user=user)
        
        # Apply filters
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        thread_id = self.request.query_params.get('thread_id')
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        
        api_session_id = self.request.query_params.get('api_session_id')
        if api_session_id:
            queryset = queryset.filter(api_session_id=api_session_id)
        
        # Filter by include flag
        include_only = self.request.query_params.get('include_only')
        if include_only and include_only.lower() == 'true':
            queryset = queryset.filter(include=True)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def stream_chat(self, request):
        """Stream chat responses using Server-Sent Events."""
        serializer = ChatStreamSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        attachments = serializer.validated_data.get('attachments', [])
        mode = serializer.validated_data.get('mode', 'chat')
        
        # Get workspace from request
        workspace_slug = request.data.get('workspace_slug')
        thread_slug = request.data.get('thread_slug')
        
        try:
            workspace = Workspace.objects.get(slug=workspace_slug)
            
            # Check user access to workspace
            if request.user.role != 'admin' and not workspace.users.filter(id=request.user.id).exists():
                return Response(
                    {'error': 'You do not have access to this workspace'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Workspace.DoesNotExist:
            return Response(
                {'error': 'Workspace not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check user chat limit
        if request.user.daily_message_limit:
            last_24_hours = timezone.now() - timedelta(hours=24)
            chat_count = WorkspaceChat.objects.filter(
                user=request.user,
                created_at__gte=last_24_hours
            ).count()
            
            if chat_count >= request.user.daily_message_limit:
                return Response(
                    {'error': f'You have reached your daily chat limit of {request.user.daily_message_limit}'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        
        # Get thread if provided
        thread = None
        thread_id = None
        if thread_slug:
            try:
                thread = WorkspaceThread.objects.get(slug=thread_slug, workspace=workspace)
                thread_id = thread.id
            except WorkspaceThread.DoesNotExist:
                pass
        
        def generate_response():
            """Generator function for streaming response."""
            chat_id = str(uuid_lib.uuid4())
            
            # Send initial message
            yield f"data: {json.dumps({'id': chat_id, 'type': 'start', 'message': 'Processing your request...'})}\n\n"
            
            # TODO: Integrate with actual LLM provider
            # For now, simulate a response
            response_text = f"This is a simulated response to: {message}"
            
            # Stream the response in chunks
            for i, char in enumerate(response_text):
                yield f"data: {json.dumps({'id': chat_id, 'type': 'stream', 'token': char})}\n\n"
            
            # Save chat to database
            chat = WorkspaceChat.objects.create(
                workspace_id=workspace.id,
                prompt=message,
                response=response_text,
                user=request.user,
                thread_id=thread_id
            )
            
            # Send completion message
            yield f"data: {json.dumps({'id': chat_id, 'type': 'complete', 'message': 'Response complete', 'chat_id': chat.id})}\n\n"
            
            # Log telemetry
            EventLog.log_event(
                'chat_sent',
                {
                    'workspace_name': workspace.name,
                    'mode': mode,
                    'has_attachments': len(attachments) > 0
                },
                request.user.id
            )
            
            Telemetry.send_telemetry(
                'chat_sent',
                {
                    'workspace_id': workspace.id,
                    'chat_mode': mode,
                    'multimodal': len(attachments) > 0
                },
                request.user.id
            )
        
        response = StreamingHttpResponse(
            generate_response(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get chat history with filters."""
        serializer = ChatHistorySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        # Apply additional filters
        if not serializer.validated_data.get('include_system', False):
            queryset = queryset.filter(include=True)
        
        # Pagination
        limit = serializer.validated_data['limit']
        offset = serializer.validated_data['offset']
        queryset = queryset[offset:offset + limit]
        
        chat_serializer = WorkspaceChatSerializer(queryset, many=True)
        
        return Response({
            'chats': chat_serializer.data,
            'total': self.get_queryset().count(),
            'limit': limit,
            'offset': offset
        })
    
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """Submit feedback for a chat."""
        serializer = ChatFeedbackSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        chat_id = serializer.validated_data['chat_id']
        feedback = serializer.validated_data['feedback']
        
        try:
            chat = WorkspaceChat.objects.get(id=chat_id, user=request.user)
            chat.feedback_score = feedback
            chat.save()
            
            EventLog.log_event(
                'chat_feedback',
                {
                    'chat_id': chat_id,
                    'feedback': 'positive' if feedback else 'negative',
                    'comment': serializer.validated_data.get('comment')
                },
                request.user.id
            )
            
            return Response({'message': 'Feedback submitted successfully'})
        
        except WorkspaceChat.DoesNotExist:
            return Response(
                {'error': 'Chat not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def export(self, request):
        """Export chat history."""
        serializer = ChatExportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        # Apply date filters
        date_from = serializer.validated_data.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = serializer.validated_data.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        format_type = serializer.validated_data['format']
        
        if format_type == 'json':
            chats = WorkspaceChatSerializer(queryset, many=True).data
            return Response({'chats': chats})
        
        elif format_type == 'csv':
            import csv
            from django.http import HttpResponse
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="chat_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['ID', 'Prompt', 'Response', 'User', 'Created At'])
            
            for chat in queryset:
                writer.writerow([
                    chat.id,
                    chat.prompt,
                    chat.response,
                    chat.user.username if chat.user else 'System',
                    chat.created_at
                ])
            
            return response
        
        else:
            return Response(
                {'error': f'Export format {format_type} not yet implemented'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search through chat history."""
        serializer = ChatSearchSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        search_in = serializer.validated_data['search_in']
        limit = serializer.validated_data['limit']
        
        queryset = self.get_queryset()
        
        # Build search query
        search_q = Q()
        if 'prompt' in search_in:
            search_q |= Q(prompt__icontains=query)
        if 'response' in search_in:
            search_q |= Q(response__icontains=query)
        
        queryset = queryset.filter(search_q)[:limit]
        
        chat_serializer = WorkspaceChatSerializer(queryset, many=True)
        
        return Response({
            'results': chat_serializer.data,
            'query': query,
            'total': queryset.count()
        })


class WelcomeMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for WelcomeMessage management."""
    queryset = WelcomeMessage.objects.all()
    serializer_class = WelcomeMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user if provided."""
        queryset = super().get_queryset()
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user=user)
        return queryset