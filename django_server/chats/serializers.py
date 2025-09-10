from rest_framework import serializers
from .models import WorkspaceChat, WelcomeMessage
from authentication.serializers import UserSerializer


class WorkspaceChatSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceChat model."""
    
    # User field should be set from request context, not from input
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WorkspaceChat
        fields = [
            'id', 'workspace_id', 'prompt', 'response', 'include',
            'user', 'username', 'thread_id', 'api_session_id',
            'feedback_score', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_updated_at', 'username']


class ChatStreamSerializer(serializers.Serializer):
    """Serializer for chat streaming requests."""
    
    message = serializers.CharField(required=True, min_length=1)
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        default=list
    )
    mode = serializers.ChoiceField(
        choices=['chat', 'query'],
        default='chat',
        required=False
    )
    temperature = serializers.FloatField(min_value=0, max_value=2, required=False, default=0.7)
    
    # File upload limits
    MAX_ATTACHMENTS = 10
    MAX_FILE_SIZE_MB = 20
    
    def validate_message(self, value):
        """Validate message content."""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Message cannot be empty")
        
        # Check message length limit (e.g., 10000 characters)
        if len(value) > 10000:
            raise serializers.ValidationError("Message is too long (max 10000 characters)")
        
        return value
    
    def validate_attachments(self, files):
        """Validate attachment files."""
        if len(files) > self.MAX_ATTACHMENTS:
            raise serializers.ValidationError(
                f"Too many attachments (max {self.MAX_ATTACHMENTS})"
            )
        
        for file in files:
            size_mb = getattr(file, 'size', 0) / (1024 * 1024)
            if size_mb > self.MAX_FILE_SIZE_MB:
                raise serializers.ValidationError(
                    f"Attachment {getattr(file, 'name', '')} exceeds {self.MAX_FILE_SIZE_MB}MB"
                )
        
        return files


class ChatHistorySerializer(serializers.Serializer):
    """Serializer for chat history requests."""
    
    workspace_id = serializers.IntegerField(required=False)
    thread_id = serializers.IntegerField(required=False)
    api_session_id = serializers.CharField(required=False)
    include_system = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)
    offset = serializers.IntegerField(default=0, min_value=0)
    
    def validate(self, attrs):
        """Ensure at least one filter is provided to prevent full table scans."""
        if not any(attrs.get(k) for k in ('workspace_id', 'thread_id', 'api_session_id')):
            raise serializers.ValidationError(
                "Provide at least one of workspace_id, thread_id, or api_session_id"
            )
        return attrs


class ChatFeedbackSerializer(serializers.Serializer):
    """Serializer for chat feedback."""
    
    chat_id = serializers.IntegerField(required=True)
    feedback = serializers.BooleanField(required=True)  # True for positive, False for negative
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)


class WelcomeMessageSerializer(serializers.ModelSerializer):
    """Serializer for WelcomeMessage model."""
    
    class Meta:
        model = WelcomeMessage
        fields = ['id', 'user', 'response', 'order_index', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatExportSerializer(serializers.Serializer):
    """Serializer for chat export requests."""
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('txt', 'Plain Text'),
        ('pdf', 'PDF'),
    ]
    
    workspace_id = serializers.IntegerField(required=False)
    thread_id = serializers.IntegerField(required=False)
    format = serializers.ChoiceField(choices=FORMAT_CHOICES, default='json')
    include_metadata = serializers.BooleanField(default=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    
    def validate(self, attrs):
        """Validate date range."""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to")
        
        return attrs


class ChatSearchSerializer(serializers.Serializer):
    """Serializer for searching chats."""
    
    query = serializers.CharField(required=True, min_length=2)
    workspace_id = serializers.IntegerField(required=False)
    thread_id = serializers.IntegerField(required=False)
    search_in = serializers.MultipleChoiceField(
        choices=['prompt', 'response'],
        default=['prompt', 'response']
    )
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)