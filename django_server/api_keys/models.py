from django.db import models
from django.contrib.auth import get_user_model
import secrets
import hashlib

User = get_user_model()


class APIKey(models.Model):
    """API keys for developer access."""
    
    id = models.BigAutoField(primary_key=True)
    secret = models.CharField(max_length=255, unique=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_keys'
    
    def __str__(self):
        return f"API Key {self.id}"
    
    @classmethod
    def generate_key(cls, created_by=None):
        """Generate a new API key."""
        # Generate a secure random key
        raw_key = secrets.token_urlsafe(32)
        # Hash it for storage
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        
        api_key = cls.objects.create(
            secret=hashed_key,
            created_by=created_by
        )
        
        # Return both the raw key (to give to user) and the object
        return raw_key, api_key
    
    @classmethod
    def verify_key(cls, raw_key):
        """Verify an API key."""
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            return cls.objects.get(secret=hashed_key)
        except cls.DoesNotExist:
            return None


class BrowserExtensionAPIKey(models.Model):
    """API keys for browser extension access."""
    
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='browser_extension_api_keys')
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'browser_extension_api_keys'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Browser Extension API Key for {self.user.username if self.user else 'Unknown'}"
    
    @classmethod
    def generate_key(cls, user=None):
        """Generate a new browser extension API key."""
        raw_key = secrets.token_urlsafe(32)
        
        api_key = cls.objects.create(
            key=raw_key,
            user=user
        )
        
        return api_key


class Invite(models.Model):
    """Invitation codes for user registration."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    claimed_by = models.IntegerField(null=True, blank=True)
    workspace_ids = models.JSONField(blank=True, null=True)  # List of workspace IDs
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invites'
    
    def __str__(self):
        return f"Invite {self.code} - {self.status}"
    
    @classmethod
    def generate_invite(cls, created_by, workspace_ids=None):
        """Generate a new invitation code."""
        code = secrets.token_urlsafe(16)
        
        invite = cls.objects.create(
            code=code,
            created_by=created_by,
            workspace_ids=workspace_ids
        )
        
        return invite
    
    def claim(self, user_id):
        """Claim an invitation."""
        if self.status != 'pending':
            return False
        
        self.status = 'claimed'
        self.claimed_by = user_id
        self.save()
        return True