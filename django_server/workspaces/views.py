from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import (
    Workspace, WorkspaceUser, WorkspaceThread, WorkspaceSuggestedMessage,
    WorkspaceAgentInvocation, SlashCommandPreset, PromptHistory, WorkspaceParsedFile
)
from .serializers import (
    WorkspaceSerializer, WorkspaceCreateSerializer, WorkspaceThreadSerializer,
    WorkspaceSuggestedMessageSerializer, WorkspaceAgentInvocationSerializer,
    SlashCommandPresetSerializer, PromptHistorySerializer, WorkspaceParsedFileSerializer,
    WorkspaceUserSerializer, WorkspaceUserCreateSerializer
)
from system_settings.models import EventLog, Telemetry


class WorkspaceViewSet(viewsets.ModelViewSet):
    """ViewSet for Workspace management."""
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkspaceCreateSerializer
        return WorkspaceSerializer
    
    def get_queryset(self):
        """Filter workspaces based on user access."""
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        return self.queryset.filter(users=user)
    
    def perform_create(self, serializer):
        """Log workspace creation."""
        workspace = serializer.save()
        
        EventLog.log_event(
            'workspace_created',
            {'workspace_name': workspace.name},
            self.request.user.id
        )
        
        Telemetry.send_telemetry(
            'workspace_created',
            {
                'workspace_id': workspace.id,
                'chat_mode': workspace.chat_mode,
            },
            self.request.user.id
        )
    
    def perform_update(self, serializer):
        """Log workspace updates."""
        workspace = serializer.save()
        
        EventLog.log_event(
            'workspace_updated',
            {'workspace_name': workspace.name, 'changes': serializer.validated_data},
            self.request.user.id
        )
    
    def perform_destroy(self, instance):
        """Log workspace deletion."""
        EventLog.log_event(
            'workspace_deleted',
            {'workspace_name': instance.name},
            self.request.user.id
        )
        super().perform_destroy(instance)
    
    @action(detail=True, methods=['get'])
    def threads(self, request, slug=None):
        """Get all threads for a workspace."""
        workspace = self.get_object()
        threads = WorkspaceThread.objects.filter(workspace=workspace)
        
        # Filter by user if not admin
        if request.user.role != 'admin':
            threads = threads.filter(Q(user=request.user) | Q(user__isnull=True))
        
        serializer = WorkspaceThreadSerializer(threads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def suggested_messages(self, request, slug=None):
        """Get suggested messages for a workspace."""
        workspace = self.get_object()
        messages = WorkspaceSuggestedMessage.objects.filter(workspace=workspace)
        serializer = WorkspaceSuggestedMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_user(self, request, slug=None):
        """Add a user to the workspace."""
        workspace = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has access
        if WorkspaceUser.objects.filter(workspace=workspace, user_id=user_id).exists():
            return Response(
                {'error': 'User already has access to this workspace'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        WorkspaceUser.objects.create(workspace=workspace, user_id=user_id)
        
        EventLog.log_event(
            'workspace_user_added',
            {'workspace_name': workspace.name, 'user_id': user_id},
            request.user.id
        )
        
        return Response({'message': 'User added successfully'})
    
    @action(detail=True, methods=['post'])
    def remove_user(self, request, slug=None):
        """Remove a user from the workspace."""
        workspace = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        WorkspaceUser.objects.filter(workspace=workspace, user_id=user_id).delete()
        
        EventLog.log_event(
            'workspace_user_removed',
            {'workspace_name': workspace.name, 'user_id': user_id},
            request.user.id
        )
        
        return Response({'message': 'User removed successfully'})
    
    @action(detail=True, methods=['get'])
    def users(self, request, slug=None):
        """Get all users with access to the workspace."""
        workspace = self.get_object()
        workspace_users = WorkspaceUser.objects.filter(workspace=workspace)
        serializer = WorkspaceUserSerializer(workspace_users, many=True)
        return Response(serializer.data)


class WorkspaceThreadViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkspaceThread management."""
    queryset = WorkspaceThread.objects.all()
    serializer_class = WorkspaceThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter threads based on user access."""
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        return self.queryset.filter(Q(user=user) | Q(user__isnull=True))
    
    def perform_create(self, serializer):
        """Set user when creating thread."""
        serializer.save(user=self.request.user)
        
        EventLog.log_event(
            'thread_created',
            {
                'thread_name': serializer.instance.name,
                'workspace_name': serializer.instance.workspace.name
            },
            self.request.user.id
        )


class WorkspaceSuggestedMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkspaceSuggestedMessage management."""
    queryset = WorkspaceSuggestedMessage.objects.all()
    serializer_class = WorkspaceSuggestedMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by workspace if provided."""
        queryset = super().get_queryset()
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        return queryset


class SlashCommandPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for SlashCommandPreset management."""
    queryset = SlashCommandPreset.objects.all()
    serializer_class = SlashCommandPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter commands by user."""
        user = self.request.user
        return self.queryset.filter(Q(user=user) | Q(uid=0))  # User's commands or global
    
    def perform_create(self, serializer):
        """Set user when creating command."""
        serializer.save(user=self.request.user, uid=self.request.user.id)


class PromptHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for PromptHistory."""
    queryset = PromptHistory.objects.all()
    serializer_class = PromptHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by workspace if provided."""
        queryset = super().get_queryset()
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set modified_by when creating."""
        serializer.save(modified_by=self.request.user)


class WorkspaceParsedFileViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkspaceParsedFile management."""
    queryset = WorkspaceParsedFile.objects.all()
    serializer_class = WorkspaceParsedFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter files based on user access."""
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        
        # Filter by workspaces user has access to
        user_workspaces = Workspace.objects.filter(users=user)
        return self.queryset.filter(workspace__in=user_workspaces)
    
    def perform_create(self, serializer):
        """Set user when creating parsed file."""
        serializer.save(user=self.request.user)