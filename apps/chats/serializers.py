from rest_framework import serializers
from typing import Optional, List, Dict, Any


class WorkspaceThreadCreateSerializer(serializers.Serializer):
    """Serializer for creating a new workspace thread"""
    userId = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(max_length=255, required=False, allow_null=True)
    slug = serializers.CharField(max_length=255, required=False, allow_null=True)


class WorkspaceThreadUpdateSerializer(serializers.Serializer):
    """Serializer for updating workspace thread"""
    name = serializers.CharField(max_length=255, required=True)


class WorkspaceThreadChatSerializer(serializers.Serializer):
    """Serializer for workspace thread chat requests"""
    message = serializers.CharField(required=True)
    mode = serializers.ChoiceField(
        choices=['query', 'chat'],
        required=False,
        default='query'
    )
    userId = serializers.IntegerField(required=False, allow_null=True)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    reset = serializers.BooleanField(required=False, default=False)


class WorkspaceThreadResponseSerializer(serializers.Serializer):
    """Serializer for workspace thread response data"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    user_id = serializers.IntegerField(allow_null=True)
    workspace_id = serializers.IntegerField()


class WorkspaceThreadListResponseSerializer(serializers.Serializer):
    """Serializer for workspace thread list response"""
    threads = serializers.ListField(
        child=WorkspaceThreadResponseSerializer(),
        required=True
    )


class WorkspaceThreadDetailResponseSerializer(serializers.Serializer):
    """Serializer for workspace thread detail response"""
    thread = serializers.ListField(
        child=WorkspaceThreadResponseSerializer(),
        required=True
    )
    message = serializers.CharField(allow_null=True)


class ChatHistoryItemSerializer(serializers.Serializer):
    """Serializer for individual chat history items"""
    role = serializers.CharField()
    content = serializers.CharField()
    sentAt = serializers.IntegerField(required=False)
    sources = serializers.ListField(required=False, default=list)


class ChatHistoryResponseSerializer(serializers.Serializer):
    """Serializer for chat history response"""
    history = serializers.ListField(
        child=ChatHistoryItemSerializer(),
        required=True
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response"""
    id = serializers.CharField()
    type = serializers.CharField()
    textResponse = serializers.CharField(allow_null=True)
    sources = serializers.ListField(default=list)
    close = serializers.BooleanField()
    error = serializers.CharField(allow_null=True)


class StreamChatChunkSerializer(serializers.Serializer):
    """Serializer for streaming chat chunks"""
    id = serializers.CharField()
    type = serializers.CharField()
    textResponse = serializers.CharField(allow_null=True)
    sources = serializers.ListField(default=list)
    close = serializers.BooleanField()
    error = serializers.CharField(allow_null=True)


class ChatFeedbackSerializer(serializers.Serializer):
    """Serializer for chat feedback"""
    feedback = serializers.CharField(required=False, allow_null=True)


class ChatUpdateSerializer(serializers.Serializer):
    """Serializer for updating chat content"""
    chatId = serializers.IntegerField(required=True)
    newText = serializers.CharField(required=True)


class ChatDeleteSerializer(serializers.Serializer):
    """Serializer for deleting chats"""
    chatIds = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )


class ChatDeleteEditedSerializer(serializers.Serializer):
    """Serializer for deleting edited chats"""
    startingId = serializers.IntegerField(required=True)


class ThreadForkSerializer(serializers.Serializer):
    """Serializer for forking a thread"""
    chatId = serializers.IntegerField(required=True)
    threadSlug = serializers.CharField(required=False, allow_null=True)


class ThreadForkResponseSerializer(serializers.Serializer):
    """Serializer for thread fork response"""
    newThreadSlug = serializers.CharField()


class ChatHideSerializer(serializers.Serializer):
    """Serializer for hiding a chat"""
    id = serializers.IntegerField(required=True)


class ChatHideResponseSerializer(serializers.Serializer):
    """Serializer for chat hide response"""
    success = serializers.BooleanField()
    error = serializers.CharField(allow_null=True)