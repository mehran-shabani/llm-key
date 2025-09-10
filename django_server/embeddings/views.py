from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import EmbedConfig, EmbedChat
from .serializers import EmbedConfigSerializer, EmbedChatSerializer
from workspaces.models import Workspace
from system_settings.models import EventLog


class EmbedConfigSerializer(serializers.ModelSerializer):
    """Serializer for EmbedConfig model."""
    
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    
    class Meta:
        model = EmbedConfig
        fields = [
            'id', 'uuid', 'enabled', 'chat_mode', 'allowlist_domains',
            'allow_model_override', 'allow_temperature_override', 'allow_prompt_override',
            'max_chats_per_day', 'max_chats_per_session', 'message_limit',
            'workspace', 'workspace_name', 'created_by', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at']


class EmbedChatSerializer(serializers.ModelSerializer):
    """Serializer for EmbedChat model."""
    
    class Meta:
        model = EmbedChat
        fields = [
            'id', 'prompt', 'response', 'session_id', 'include',
            'connection_information', 'embed_config', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmbedConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for EmbedConfig management."""
    queryset = EmbedConfig.objects.all()
    serializer_class = EmbedConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'
    
    def get_queryset(self):
        """Filter configs based on user access."""
        user = self.request.user
        if user.role == 'admin':
            return self.queryset
        
        # Get workspaces user has access to
        user_workspaces = Workspace.objects.filter(users=user)
        return self.queryset.filter(workspace__in=user_workspaces)
    
    def perform_create(self, serializer):
        """Set created_by when creating config."""
        serializer.save(
            created_by=self.request.user.id,
            user=self.request.user
        )
        
        EventLog.log_event(
            'embed_config_created',
            {'workspace_id': serializer.instance.workspace.id},
            self.request.user.id
        )
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, uuid=None):
        """Toggle embed config enabled status."""
        config = self.get_object()
        config.enabled = not config.enabled
        config.save()
        
        EventLog.log_event(
            'embed_config_toggled',
            {
                'workspace_name': config.workspace.name,
                'enabled': config.enabled
            },
            request.user.id
        )
        
        return Response({'enabled': config.enabled})
    
    @action(detail=True, methods=['get'])
    def embed_code(self, request, uuid=None):
        """Generate embed code for the configuration."""
        config = self.get_object()
        
        if not config.enabled:
            return Response(
                {'error': 'Embed configuration is not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate embed code
        embed_code = f'''
<script>
  (function() {{
    var script = document.createElement('script');
    script.src = '{request.build_absolute_uri("/")}/static/embed.js';
    script.setAttribute('data-embed-id', '{config.uuid}');
    script.setAttribute('data-base-url', '{request.build_absolute_uri("/")}');
    document.head.appendChild(script);
  }})();
</script>
<div id="anythingllm-embed-{config.uuid}"></div>
        '''
        
        return Response({
            'embed_code': embed_code.strip(),
            'uuid': str(config.uuid),
            'workspace': config.workspace.name
        })


class EmbedChatViewSet(viewsets.ModelViewSet):
    """ViewSet for EmbedChat management."""
    queryset = EmbedChat.objects.all()
    serializer_class = EmbedChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter chats based on embed config access."""
        user = self.request.user
        
        if user.role == 'admin':
            queryset = self.queryset
        else:
            # Get configs user has access to
            user_workspaces = Workspace.objects.filter(users=user)
            user_configs = EmbedConfig.objects.filter(workspace__in=user_workspaces)
            queryset = self.queryset.filter(embed_config__in=user_configs)
        
        # Filter by session_id if provided
        session_id = self.request.query_params.get('session_id')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # Filter by embed_config if provided
        embed_config_uuid = self.request.query_params.get('embed_config')
        if embed_config_uuid:
            queryset = queryset.filter(embed_config__uuid=embed_config_uuid)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """Get unique session IDs for embed chats."""
        queryset = self.get_queryset()
        
        # Get unique session IDs
        sessions = queryset.values_list('session_id', flat=True).distinct()
        
        # Get session statistics
        session_stats = []
        for session_id in sessions:
            session_chats = queryset.filter(session_id=session_id)
            first_chat = session_chats.first()
            last_chat = session_chats.last()
            
            session_stats.append({
                'session_id': session_id,
                'chat_count': session_chats.count(),
                'first_chat': first_chat.created_at if first_chat else None,
                'last_chat': last_chat.created_at if last_chat else None,
                'embed_config': str(first_chat.embed_config.uuid) if first_chat else None
            })
        
        return Response({
            'sessions': session_stats,
            'total': len(sessions)
        })


# Import serializers at the end to avoid circular imports
from rest_framework import serializers