from rest_framework import serializers
from apps.coredb.models import User, Invite, Workspace, WorkspaceUser, WorkspaceChat


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'suspended', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    
    class Meta:
        model = User
        fields = ['username', 'password', 'role']
        
    def create(self, validated_data):
        # In a real implementation, you'd hash the password
        return User.objects.create(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users"""
    
    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'suspended']


class InviteSerializer(serializers.ModelSerializer):
    """Serializer for Invite model"""
    
    class Meta:
        model = Invite
        fields = ['id', 'code', 'status', 'claimed_by', 'workspace_ids', 'created_at', 'created_by']
        read_only_fields = ['id', 'code', 'created_at', 'created_by']


class InviteCreateSerializer(serializers.Serializer):
    """Serializer for creating invites"""
    workspace_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )


class WorkspaceUserSerializer(serializers.Serializer):
    """Serializer for workspace users"""
    user_id = serializers.IntegerField()
    username = serializers.CharField(required=False)
    role = serializers.CharField(required=False)


class WorkspaceUsersUpdateSerializer(serializers.Serializer):
    """Serializer for updating workspace users"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )


class WorkspaceUsersManageSerializer(serializers.Serializer):
    """Serializer for managing workspace users"""
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    reset = serializers.BooleanField(default=False)


class WorkspaceChatSerializer(serializers.ModelSerializer):
    """Serializer for workspace chats"""
    
    class Meta:
        model = WorkspaceChat
        fields = ['id', 'workspace_id', 'prompt', 'response', 'include', 'user_id', 'thread_id', 'api_session_id', 'created_at', 'feedback_score']
        read_only_fields = ['id', 'created_at']


class WorkspaceChatsListSerializer(serializers.Serializer):
    """Serializer for workspace chats list request"""
    offset = serializers.IntegerField(default=0, min_value=0)


class SystemPreferencesSerializer(serializers.Serializer):
    """Serializer for system preferences"""
    support_email = serializers.EmailField(required=False)
    # Add other preference fields as needed


class MultiUserModeSerializer(serializers.Serializer):
    """Serializer for multi-user mode response"""
    is_multi_user = serializers.BooleanField()


class SuccessResponseSerializer(serializers.Serializer):
    """Generic success response serializer"""
    success = serializers.BooleanField()
    error = serializers.CharField(allow_null=True)


class UserResponseSerializer(serializers.Serializer):
    """Serializer for user response"""
    user = UserSerializer(allow_null=True)
    error = serializers.CharField(allow_null=True)


class InviteResponseSerializer(serializers.Serializer):
    """Serializer for invite response"""
    invite = InviteSerializer(allow_null=True)
    error = serializers.CharField(allow_null=True)


class WorkspaceUsersResponseSerializer(serializers.Serializer):
    """Serializer for workspace users response"""
    users = WorkspaceUserSerializer(many=True)


class WorkspaceChatsResponseSerializer(serializers.Serializer):
    """Serializer for workspace chats response"""
    chats = WorkspaceChatSerializer(many=True)
    has_pages = serializers.BooleanField()