from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import User, RecoveryCode, PasswordResetToken, TemporaryAuthToken, DesktopMobileDevice
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetSerializer, RecoveryCodeSerializer, TemporaryAuthTokenSerializer,
    DesktopMobileDeviceSerializer
)
from system_settings.models import EventLog


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with event logging."""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                EventLog.log_event(
                    'login_event',
                    {'ip': request.META.get('REMOTE_ADDR', 'Unknown IP'), 'username': username},
                    user.id
                )
            except User.DoesNotExist:
                pass
        
        return response


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Allow unauthenticated users to register in non-multi-user mode
            from django.conf import settings
            if not settings.MULTI_USER_MODE:
                return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            # Only admins can list all users or delete users
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user information."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            EventLog.log_event(
                'password_changed',
                {'username': user.username},
                user.id
            )
            
            return Response({'message': 'Password changed successfully.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def request_password_reset(self, request):
        """Request password reset token."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            try:
                user = User.objects.get(username=username)
                
                # Create reset token
                token = secrets.token_urlsafe(32)
                expires_at = timezone.now() + timedelta(hours=1)
                
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )
                
                # In production, send email with token
                # For now, just log it
                EventLog.log_event(
                    'password_reset_requested',
                    {'username': username},
                    user.id
                )
                
            except User.DoesNotExist:
                pass  # Don't reveal if user exists
            
            return Response({'message': 'If the username exists, a password reset link has been sent.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password(self, request):
        """Reset password with token."""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            reset_token = PasswordResetToken.objects.get(token=token)
            
            user = reset_token.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete the used token
            reset_token.delete()
            
            EventLog.log_event(
                'password_reset_completed',
                {'username': user.username},
                user.id
            )
            
            return Response({'message': 'Password reset successfully.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generate_recovery_codes(self, request):
        """Generate recovery codes for two-factor authentication."""
        user = request.user
        
        # Delete existing recovery codes
        RecoveryCode.objects.filter(user=user).delete()
        
        # Generate new codes
        codes = []
        for _ in range(10):
            code = secrets.token_hex(8)
            RecoveryCode.objects.create(
                user=user,
                code_hash=code  # In production, hash this
            )
            codes.append(code)
        
        user.seen_recovery_codes = True
        user.save()
        
        EventLog.log_event(
            'recovery_codes_generated',
            {'username': user.username},
            user.id
        )
        
        return Response({'codes': codes})
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Logout user."""
        EventLog.log_event(
            'logout_event',
            {'username': request.user.username},
            request.user.id
        )
        logout(request)
        return Response({'message': 'Logged out successfully.'})


class DesktopMobileDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for desktop/mobile device connections."""
    queryset = DesktopMobileDevice.objects.all()
    serializer_class = DesktopMobileDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter devices by current user."""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating device."""
        token = secrets.token_urlsafe(32)
        serializer.save(user=self.request.user, token=token)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a device connection."""
        device = self.get_object()
        device.approved = True
        device.save()
        
        EventLog.log_event(
            'device_approved',
            {'device_name': device.device_name, 'device_os': device.device_os},
            request.user.id
        )
        
        return Response({'message': 'Device approved successfully.'})
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a device connection."""
        device = self.get_object()
        device.approved = False
        device.save()
        
        EventLog.log_event(
            'device_revoked',
            {'device_name': device.device_name, 'device_os': device.device_os},
            request.user.id
        )
        
        return Response({'message': 'Device revoked successfully.'})


class IsAdminUser(permissions.BasePermission):
    """Permission class to check if user is admin."""
    
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'