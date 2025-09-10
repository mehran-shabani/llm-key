from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, RecoveryCode, PasswordResetToken, TemporaryAuthToken, DesktopMobileDevice


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'pfp_filename': self.user.pfp_filename,
            'suspended': self.user.suspended,
        }
        
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'pfp_filename', 'role', 
            'suspended', 'daily_message_limit', 'bio', 
            'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = ['email', 'pfp_filename', 'bio', 'daily_message_limit']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    
    username = serializers.CharField(required=True)
    
    def validate_username(self, value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            # Don't reveal if user exists or not
            pass
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for resetting password with token."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        
        try:
            reset_token = PasswordResetToken.objects.get(token=attrs['token'])
            if not reset_token.is_valid():
                raise serializers.ValidationError({"token": "Token has expired."})
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})
        
        return attrs


class RecoveryCodeSerializer(serializers.ModelSerializer):
    """Serializer for recovery codes."""
    
    class Meta:
        model = RecoveryCode
        fields = ['id', 'code_hash', 'created_at']
        read_only_fields = ['id', 'code_hash', 'created_at']


class TemporaryAuthTokenSerializer(serializers.ModelSerializer):
    """Serializer for temporary auth tokens."""
    
    class Meta:
        model = TemporaryAuthToken
        fields = ['id', 'token', 'expires_at', 'created_at']
        read_only_fields = ['id', 'token', 'created_at']


class DesktopMobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for desktop/mobile device connections."""
    
    class Meta:
        model = DesktopMobileDevice
        fields = ['id', 'device_os', 'device_name', 'token', 'approved', 'created_at']
        read_only_fields = ['id', 'token', 'created_at']