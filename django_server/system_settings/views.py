from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.db import connection
from django.utils import timezone
import platform
import psutil
import os

from .models import SystemSetting, SystemPromptVariable, EventLog, Telemetry, CacheData
from .serializers import (
    SystemSettingSerializer, SystemPromptVariableSerializer,
    EventLogSerializer, TelemetrySerializer, CacheDataSerializer
)


class SystemSettingSerializer(serializers.ModelSerializer):
    """Serializer for SystemSetting model."""
    
    class Meta:
        model = SystemSetting
        fields = ['id', 'label', 'value', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class SystemPromptVariableSerializer(serializers.ModelSerializer):
    """Serializer for SystemPromptVariable model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SystemPromptVariable
        fields = [
            'id', 'key', 'value', 'description', 'type',
            'user', 'username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventLogSerializer(serializers.ModelSerializer):
    """Serializer for EventLog model."""
    
    class Meta:
        model = EventLog
        fields = ['id', 'event', 'metadata', 'user_id', 'occurred_at']
        read_only_fields = ['id', 'occurred_at']


class TelemetrySerializer(serializers.ModelSerializer):
    """Serializer for Telemetry model."""
    
    class Meta:
        model = Telemetry
        fields = ['id', 'event', 'data', 'user_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class CacheDataSerializer(serializers.ModelSerializer):
    """Serializer for CacheData model."""
    
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CacheData
        fields = [
            'id', 'name', 'data', 'belongs_to', 'by_id',
            'expires_at', 'is_expired', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'is_expired', 'created_at', 'last_updated_at']


class IsAdminUser(permissions.BasePermission):
    """Permission class to check if user is admin."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class SystemSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for SystemSetting management."""
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'label'
    
    def perform_update(self, serializer):
        """Log setting changes."""
        setting = serializer.save()
        
        EventLog.log_event(
            'system_setting_changed',
            {
                'label': setting.label,
                'value': setting.value
            },
            self.request.user.id
        )


class SystemPromptVariableViewSet(viewsets.ModelViewSet):
    """ViewSet for SystemPromptVariable management."""
    queryset = SystemPromptVariable.objects.all()
    serializer_class = SystemPromptVariableSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'key'
    
    def get_queryset(self):
        """Filter variables based on type and user."""
        queryset = super().get_queryset()
        
        # Filter by type
        var_type = self.request.query_params.get('type')
        if var_type:
            queryset = queryset.filter(type=var_type)
        
        # Non-admins can only see system variables and their own user variables
        if self.request.user.role != 'admin':
            from django.db.models import Q
            queryset = queryset.filter(
                Q(type='system') | Q(user=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set user for user-type variables."""
        var_type = serializer.validated_data.get('type', 'system')
        if var_type == 'user':
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for EventLog (read-only)."""
    queryset = EventLog.objects.all()
    serializer_class = EventLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter event logs."""
        queryset = super().get_queryset()
        
        # Filter by event type
        event = self.request.query_params.get('event')
        if event:
            queryset = queryset.filter(event=event)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        if from_date:
            queryset = queryset.filter(occurred_at__gte=from_date)
        
        to_date = self.request.query_params.get('to_date')
        if to_date:
            queryset = queryset.filter(occurred_at__lte=to_date)
        
        return queryset


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Telemetry (read-only)."""
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter telemetry data."""
        queryset = super().get_queryset()
        
        # Filter by event
        event = self.request.query_params.get('event')
        if event:
            queryset = queryset.filter(event=event)
        
        return queryset


class CacheDataViewSet(viewsets.ModelViewSet):
    """ViewSet for CacheData management."""
    queryset = CacheData.objects.all()
    serializer_class = CacheDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter cache data and exclude expired entries."""
        queryset = super().get_queryset()
        
        # Exclude expired entries unless requested
        include_expired = self.request.query_params.get('include_expired', 'false').lower() == 'true'
        if not include_expired:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        # Filter by name
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name=name)
        
        # Filter by belongs_to
        belongs_to = self.request.query_params.get('belongs_to')
        if belongs_to:
            queryset = queryset.filter(belongs_to=belongs_to)
        
        return queryset


class SystemStatusView(APIView):
    """View for system status information."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get system status information."""
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get database status
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Get application status
        status_data = {
            'status': 'online',
            'version': '1.0.0',
            'environment': settings.DEBUG and 'development' or 'production',
            'system': {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                }
            },
            'database': {
                'status': db_status,
                'engine': settings.DATABASES['default']['ENGINE']
            },
            'settings': {
                'multi_user_mode': settings.MULTI_USER_MODE,
                'telemetry_enabled': settings.TELEMETRY_ENABLED,
                'llm_provider': settings.LLM_PROVIDER,
                'embedding_engine': settings.EMBEDDING_ENGINE,
                'vector_db': settings.VECTOR_DB
            },
            'timestamp': timezone.now()
        }
        
        return Response(status_data)


class SetupCompleteView(APIView):
    """View to check if initial setup is complete."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Check if setup is complete."""
        from authentication.models import User
        
        setup_complete = {
            'multi_user_mode': settings.MULTI_USER_MODE,
            'has_users': User.objects.exists(),
            'has_admin': User.objects.filter(role='admin').exists(),
            'llm_configured': bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY),
            'vector_db_configured': bool(settings.VECTOR_DB),
        }
        
        setup_complete['is_complete'] = all([
            setup_complete['has_users'],
            setup_complete['has_admin'] if settings.MULTI_USER_MODE else True,
            setup_complete['llm_configured']
        ])
        
        return Response(setup_complete)


# Import serializers at the end to avoid circular imports
from rest_framework import serializers