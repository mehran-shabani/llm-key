from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for AnythingLLM."""
    
    def create_user(self, username, password=None, **extra_fields):
        """Create and save a regular user."""
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for AnythingLLM."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('default', 'Default User'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    pfp_filename = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='default')
    suspended = models.BooleanField(default=False)
    seen_recovery_codes = models.BooleanField(default=False)
    daily_message_limit = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    
    # Django required fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def can_send_chat(self):
        """Check if user can send a chat based on daily limit."""
        if not self.daily_message_limit:
            return True
        
        from chats.models import WorkspaceChat
        from django.utils import timezone
        from datetime import timedelta
        
        last_24_hours = timezone.now() - timedelta(hours=24)
        chat_count = WorkspaceChat.objects.filter(
            user=self,
            created_at__gte=last_24_hours
        ).count()
        
        return chat_count < self.daily_message_limit


class RecoveryCode(models.Model):
    """Recovery codes for two-factor authentication."""
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recovery_codes')
    code_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recovery_codes'
        indexes = [
            models.Index(fields=['user']),
        ]


class PasswordResetToken(models.Model):
    """Password reset tokens for users."""
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_reset_tokens'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def is_valid(self):
        """Check if token is still valid."""
        return timezone.now() < self.expires_at


class TemporaryAuthToken(models.Model):
    """Temporary authentication tokens for special purposes."""
    
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporary_auth_tokens')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temporary_auth_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user']),
        ]
    
    def is_valid(self):
        """Check if token is still valid."""
        return timezone.now() < self.expires_at


class DesktopMobileDevice(models.Model):
    """Mobile device connections for desktop app."""
    
    id = models.BigAutoField(primary_key=True)
    device_os = models.CharField(max_length=50)
    device_name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    approved = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='mobile_devices')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'desktop_mobile_devices'
        indexes = [
            models.Index(fields=['user']),
        ]