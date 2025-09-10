from rest_framework import serializers
from .models import (
    Workspace, WorkspaceUser, WorkspaceThread, WorkspaceSuggestedMessage,
    WorkspaceAgentInvocation, SlashCommandPreset, PromptHistory, WorkspaceParsedFile
)
from authentication.serializers import UserSerializer


class WorkspaceSerializer(serializers.ModelSerializer):
    """Serializer for Workspace model."""
    
    user_count = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'vector_tag', 'openai_temp', 'openai_history',
            'openai_prompt', 'similarity_threshold', 'chat_provider', 'chat_model',
            'top_n', 'chat_mode', 'agent_provider', 'agent_model', 'pfp_filename',
            'query_refusal_response', 'vector_search_mode', 'user_count',
            'document_count', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'last_updated_at']
    
    def get_user_count(self, obj):
        return obj.users.count()
    
    def get_document_count(self, obj):
        return obj.documents.count()


class WorkspaceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating workspaces."""
    
    class Meta:
        model = Workspace
        fields = ['name', 'openai_prompt', 'chat_mode']
    
    def create(self, validated_data):
        workspace = super().create(validated_data)
        
        # Add creator as workspace user if in multi-user mode
        user = self.context['request'].user
        if user and user.is_authenticated:
            WorkspaceUser.objects.create(workspace=workspace, user=user)
        
        return workspace


class WorkspaceThreadSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceThread model."""
    
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = WorkspaceThread
        fields = [
            'id', 'name', 'slug', 'workspace', 'workspace_name', 'user',
            'username', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'last_updated_at']


class WorkspaceSuggestedMessageSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceSuggestedMessage model."""
    
    class Meta:
        model = WorkspaceSuggestedMessage
        fields = ['id', 'workspace', 'heading', 'message', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class WorkspaceAgentInvocationSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceAgentInvocation model."""
    
    class Meta:
        model = WorkspaceAgentInvocation
        fields = [
            'id', 'uuid', 'prompt', 'closed', 'user', 'thread_id',
            'workspace', 'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'last_updated_at']


class SlashCommandPresetSerializer(serializers.ModelSerializer):
    """Serializer for SlashCommandPreset model."""
    
    class Meta:
        model = SlashCommandPreset
        fields = [
            'id', 'command', 'prompt', 'description', 'uid', 'user',
            'created_at', 'last_updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class PromptHistorySerializer(serializers.ModelSerializer):
    """Serializer for PromptHistory model."""
    
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    
    class Meta:
        model = PromptHistory
        fields = [
            'id', 'workspace', 'prompt', 'modified_by', 'modified_by_username',
            'modified_at'
        ]
        read_only_fields = ['id', 'modified_at']


class WorkspaceParsedFileSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceParsedFile model."""
    
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    thread_name = serializers.CharField(source='thread.name', read_only=True)
    
    class Meta:
        model = WorkspaceParsedFile
        fields = [
            'id', 'filename', 'workspace', 'workspace_name', 'user', 'username',
            'thread', 'thread_name', 'metadata', 'token_count_estimate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkspaceUserSerializer(serializers.ModelSerializer):
    """Serializer for WorkspaceUser model."""
    
    user = UserSerializer(read_only=True)
    workspace = WorkspaceSerializer(read_only=True)
    
    class Meta:
        model = WorkspaceUser
        fields = ['id', 'user', 'workspace', 'created_at', 'last_updated_at']
        read_only_fields = ['id', 'created_at', 'last_updated_at']


class WorkspaceUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding users to workspaces."""
    
    class Meta:
        model = WorkspaceUser
        fields = ['user', 'workspace']