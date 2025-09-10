from rest_framework import serializers


class TextGenerationSerializer(serializers.Serializer):
    """Serializer for text generation requests."""
    model = serializers.CharField(required=False, help_text="Model name (optional)")
    messages = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of messages for the conversation"
    )
    temperature = serializers.FloatField(required=False, default=0.7, min_value=0, max_value=2)
    max_tokens = serializers.IntegerField(required=False, min_value=1)
    top_p = serializers.FloatField(required=False, min_value=0, max_value=1)
    frequency_penalty = serializers.FloatField(required=False, min_value=-2, max_value=2)
    presence_penalty = serializers.FloatField(required=False, min_value=-2, max_value=2)
    stop = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of stop sequences"
    )


class TextInstructionSerializer(serializers.Serializer):
    """Serializer for text instruction requests."""
    model = serializers.CharField(required=False, help_text="Model name (optional)")
    messages = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of messages for the conversation"
    )
    temperature = serializers.FloatField(required=False, default=0.7, min_value=0, max_value=2)
    max_tokens = serializers.IntegerField(required=False, min_value=1)
    top_p = serializers.FloatField(required=False, min_value=0, max_value=1)
    frequency_penalty = serializers.FloatField(required=False, min_value=-2, max_value=2)
    presence_penalty = serializers.FloatField(required=False, min_value=-2, max_value=2)
    stop = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of stop sequences"
    )


class TextGenerationResponseSerializer(serializers.Serializer):
    """Serializer for text generation responses."""
    content = serializers.CharField(help_text="Generated text content")
    usage = serializers.DictField(required=False, help_text="Token usage information")