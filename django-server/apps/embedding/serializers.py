from rest_framework import serializers


class EmbeddingSerializer(serializers.Serializer):
    """Serializer for embedding generation requests."""
    model = serializers.CharField(required=False, help_text="Model name (optional)")
    input = serializers.CharField(help_text="Text to generate embedding for")
    encoding_format = serializers.CharField(required=False, default="float", help_text="Encoding format for the embedding")


class EmbeddingResponseSerializer(serializers.Serializer):
    """Serializer for embedding generation responses."""
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        help_text="The embedding vector"
    )
    usage = serializers.DictField(required=False, help_text="Token usage information")