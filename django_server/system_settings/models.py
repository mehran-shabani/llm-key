from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class SystemSetting(models.Model):
    """System-wide settings."""
    
    id = models.BigAutoField(primary_key=True)
    label = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
    
    def __str__(self):
        return f"{self.label}: {self.value}"
    
    @classmethod
    def get_setting(cls, label, default=None):
        """Get a system setting value with caching."""
        cache_key = f'system_setting_{label}'
        value = cache.get(cache_key)
        
        if value is None:
            try:
                setting = cls.objects.get(label=label)
                value = setting.value
                cache.set(cache_key, value, 300)  # Cache for 5 minutes
            except cls.DoesNotExist:
                value = default
        
        return value
    
    @classmethod
    def set_setting(cls, label, value):
        """Set a system setting value."""
        setting, created = cls.objects.update_or_create(
            label=label,
            defaults={'value': value}
        )
        cache.delete(f'system_setting_{label}')
        return setting
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'system_setting_{self.label}')


class SystemPromptVariable(models.Model):
    """System prompt variables for customization."""
    
    TYPE_CHOICES = [
        ('system', 'System'),
        ('user', 'User'),
        ('dynamic', 'Dynamic'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='system_prompt_variables')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_prompt_variables'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class EventLog(models.Model):
    """Event logging for auditing."""
    
    id = models.BigAutoField(primary_key=True)
    event = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, null=True)
    user_id = models.IntegerField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'event_logs'
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['user_id']),
            models.Index(fields=['occurred_at']),
        ]
        ordering = ['-occurred_at']
    
    def __str__(self):
        return f"{self.event} at {self.occurred_at}"
    
    @classmethod
    def log_event(cls, event, metadata=None, user_id=None):
        """Helper method to log an event."""
        return cls.objects.create(
            event=event,
            metadata=metadata,
            user_id=user_id
        )


class CacheData(models.Model):
    """Cache data storage."""
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    data = models.TextField()
    belongs_to = models.CharField(max_length=255, blank=True, null=True)
    by_id = models.IntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cache_data'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['belongs_to']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Cache: {self.name}"
    
    @property
    def is_expired(self):
        """Check if cache entry is expired."""
        from django.utils import timezone
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class Telemetry(models.Model):
    """Telemetry data for analytics."""
    
    id = models.BigAutoField(primary_key=True)
    event = models.CharField(max_length=255)
    data = models.JSONField(blank=True, null=True)
    user_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'telemetry'
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['created_at']),
        ]
    
    @classmethod
    def send_telemetry(cls, event, data=None, user_id=None):
        """Send telemetry data if enabled."""
        from django.conf import settings
        
        if not settings.TELEMETRY_ENABLED:
            return None
        
        return cls.objects.create(
            event=event,
            data=data,
            user_id=user_id
        )