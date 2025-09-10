from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings

from .models import APIKey, BrowserExtensionAPIKey, Invite
from .serializers import (
    APIKeySerializer, BrowserExtensionAPIKeySerializer,
    InviteSerializer, InviteClaimSerializer
)
from system_settings.models import EventLog


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model."""
    
    class Meta:
        model = APIKey
        fields = ['id', 'created_by', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class BrowserExtensionAPIKeySerializer(serializers.ModelSerializer):
    """Serializer for BrowserExtensionAPIKey model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BrowserExtensionAPIKey
        fields = ['id', 'key', 'user', 'username', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'key', 'created_at', 'last_updated_at']


class InviteSerializer(serializers.ModelSerializer):
    """Serializer for Invite model."""
    
    class Meta:
        model = Invite
        fields = [
            'id', 'code', 'status', 'claimed_by', 'workspace_ids',
            'created_at', 'created_by', 'last_updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'last_updated_at']


class InviteClaimSerializer(serializers.Serializer):
    """Serializer for claiming an invite."""
    
    code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=False)


class IsAdminUser(permissions.BasePermission):
    """Permission class to check if user is admin."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for APIKey management."""
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new API key."""
        raw_key, api_key = APIKey.generate_key(created_by=request.user.id)
        
        EventLog.log_event(
            'api_key_generated',
            {'key_id': api_key.id},
            request.user.id
        )
        
        return Response({
            'key': raw_key,
            'id': api_key.id,
            'message': 'Save this key securely. It will not be shown again.'
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify an API key."""
        key = request.data.get('key')
        
        if not key:
            return Response(
                {'error': 'API key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        api_key = APIKey.verify_key(key)
        
        if api_key:
            return Response({
                'valid': True,
                'key_id': api_key.id,
                'created_at': api_key.created_at
            })
        else:
            return Response({
                'valid': False,
                'error': 'Invalid API key'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    def perform_destroy(self, instance):
        """Log API key deletion."""
        EventLog.log_event(
            'api_key_deleted',
            {'key_id': instance.id},
            self.request.user.id
        )
        super().perform_destroy(instance)


class BrowserExtensionAPIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for BrowserExtensionAPIKey management."""
    queryset = BrowserExtensionAPIKey.objects.all()
    serializer_class = BrowserExtensionAPIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter keys by current user."""
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new browser extension API key."""
        # Delete existing key for user
        BrowserExtensionAPIKey.objects.filter(user=request.user).delete()
        
        # Generate new key
        api_key = BrowserExtensionAPIKey.generate_key(user=request.user)
        
        EventLog.log_event(
            'browser_extension_key_generated',
            {'user': request.user.username},
            request.user.id
        )
        
        serializer = self.get_serializer(api_key)
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        """Log browser extension key deletion."""
        EventLog.log_event(
            'browser_extension_key_deleted',
            {'user': instance.user.username if instance.user else 'Unknown'},
            self.request.user.id
        )
        super().perform_destroy(instance)


class InviteViewSet(viewsets.ModelViewSet):
    """ViewSet for Invite management."""
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'code'
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new invite code."""
        workspace_ids = request.data.get('workspace_ids', [])
        
        invite = Invite.generate_invite(
            created_by=request.user.id,
            workspace_ids=workspace_ids
        )
        
        EventLog.log_event(
            'invite_generated',
            {
                'code': invite.code,
                'workspace_ids': workspace_ids
            },
            request.user.id
        )
        
        serializer = self.get_serializer(invite)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def claim(self, request):
        """Claim an invite code and create user account."""
        serializer = InviteClaimSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        
        try:
            invite = Invite.objects.get(code=code, status='pending')
        except Invite.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired invite code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user account
        from authentication.models import User
        from workspaces.models import WorkspaceUser
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            email=serializer.validated_data.get('email')
        )
        
        # Claim the invite
        invite.claim(user.id)
        
        # Add user to workspaces if specified
        if invite.workspace_ids:
            for workspace_id in invite.workspace_ids:
                WorkspaceUser.objects.create(
                    user=user,
                    workspace_id=workspace_id
                )
        
        EventLog.log_event(
            'invite_claimed',
            {
                'code': code,
                'username': user.username,
                'workspace_ids': invite.workspace_ids
            },
            user.id
        )
        
        return Response({
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, code=None):
        """Revoke an invite code."""
        invite = self.get_object()
        
        if invite.status != 'pending':
            return Response(
                {'error': 'Cannot revoke a claimed or expired invite'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invite.status = 'expired'
        invite.save()
        
        EventLog.log_event(
            'invite_revoked',
            {'code': invite.code},
            request.user.id
        )
        
        return Response({'message': 'Invite revoked successfully'})


# Import serializers at the end to avoid circular imports
from rest_framework import serializers