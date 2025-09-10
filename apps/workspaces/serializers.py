from rest_framework import serializers
from typing import Optional, List, Dict, Any


class WorkspaceCreateSerializer(serializers.Serializer):
    """Serializer for creating a new workspace"""
    name = serializers.CharField(max_length=255, required=False, allow_null=True)
    similarityThreshold = serializers.FloatField(required=False, allow_null=True)
    openAiTemp = serializers.FloatField(required=False, allow_null=True)
    openAiHistory = serializers.IntegerField(required=False, allow_null=True)
    openAiPrompt = serializers.CharField(required=False, allow_null=True)
    queryRefusalResponse = serializers.CharField(required=False, allow_null=True)
    chatMode = serializers.CharField(required=False, allow_null=True)
    topN = serializers.IntegerField(required=False, allow_null=True)


class WorkspaceUpdateSerializer(serializers.Serializer):
    """Serializer for updating workspace settings"""
    name = serializers.CharField(max_length=255, required=False, allow_null=True)
    openAiTemp = serializers.FloatField(required=False, allow_null=True)
    openAiHistory = serializers.IntegerField(required=False, allow_null=True)
    openAiPrompt = serializers.CharField(required=False, allow_null=True)
    similarityThreshold = serializers.FloatField(required=False, allow_null=True)
    topN = serializers.IntegerField(required=False, allow_null=True)
    chatMode = serializers.CharField(required=False, allow_null=True)
    queryRefusalResponse = serializers.CharField(required=False, allow_null=True)


class WorkspaceEmbeddingsUpdateSerializer(serializers.Serializer):
    """Serializer for updating workspace embeddings"""
    adds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    deletes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class WorkspacePinUpdateSerializer(serializers.Serializer):
    """Serializer for updating document pin status"""
    docPath = serializers.CharField(required=True)
    pinStatus = serializers.BooleanField(required=False, default=False)


class WorkspaceChatSerializer(serializers.Serializer):
    """Serializer for workspace chat requests"""
    message = serializers.CharField(required=True)
    mode = serializers.ChoiceField(
        choices=['query', 'chat'],
        required=False,
        default='query'
    )
    sessionId = serializers.CharField(required=False, allow_null=True)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    reset = serializers.BooleanField(required=False, default=False)


class WorkspaceVectorSearchSerializer(serializers.Serializer):
    """Serializer for vector similarity search"""
    query = serializers.CharField(required=True)
    topN = serializers.IntegerField(required=False, allow_null=True)
    scoreThreshold = serializers.FloatField(required=False, allow_null=True)


class WorkspaceChatHistorySerializer(serializers.Serializer):
    """Serializer for workspace chat history parameters"""
    apiSessionId = serializers.CharField(required=False, allow_null=True)
    limit = serializers.IntegerField(required=False, default=100)
    orderBy = serializers.ChoiceField(
        choices=['asc', 'desc'],
        required=False,
        default='asc'
    )


class WorkspaceResponseSerializer(serializers.Serializer):
    """Serializer for workspace response data"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    createdAt = serializers.DateTimeField()
    lastUpdatedAt = serializers.DateTimeField()
    openAiTemp = serializers.FloatField(allow_null=True)
    openAiHistory = serializers.IntegerField(allow_null=True)
    openAiPrompt = serializers.CharField(allow_null=True)
    similarityThreshold = serializers.FloatField(allow_null=True)
    topN = serializers.IntegerField(allow_null=True)
    chatMode = serializers.CharField(allow_null=True)
    documents = serializers.ListField(required=False, default=list)
    threads = serializers.ListField(required=False, default=list)


class WorkspaceListResponseSerializer(serializers.Serializer):
    """Serializer for workspace list response"""
    workspaces = serializers.ListField(
        child=WorkspaceResponseSerializer(),
        required=True
    )


class WorkspaceDetailResponseSerializer(serializers.Serializer):
    """Serializer for workspace detail response"""
    workspace = serializers.ListField(
        child=WorkspaceResponseSerializer(),
        required=True
    )


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


class VectorSearchResultSerializer(serializers.Serializer):
    """Serializer for vector search results"""
    id = serializers.CharField()
    text = serializers.CharField()
    metadata = serializers.DictField()
    distance = serializers.FloatField()
    score = serializers.FloatField()


class VectorSearchResponseSerializer(serializers.Serializer):
    """Serializer for vector search response"""
    results = serializers.ListField(
        child=VectorSearchResultSerializer(),
        required=True
    )
    message = serializers.CharField(required=False, allow_null=True)