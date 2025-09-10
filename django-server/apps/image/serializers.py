from rest_framework import serializers


class ImageGenerationSerializer(serializers.Serializer):
    """Serializer for image generation requests."""
    model = serializers.CharField(required=False, help_text="Model name (optional)")
    prompt = serializers.CharField(help_text="Text prompt for image generation")
    n = serializers.IntegerField(required=False, default=1, min_value=1, max_value=10, help_text="Number of images to generate")
    size = serializers.CharField(required=False, default="1024x1024", help_text="Size of the generated image")
    quality = serializers.CharField(required=False, default="standard", help_text="Quality of the generated image")
    style = serializers.CharField(required=False, help_text="Style of the generated image")
    user = serializers.CharField(required=False, help_text="User identifier for tracking")


class ImageGenerationResponseSerializer(serializers.Serializer):
    """Serializer for image generation responses."""
    url = serializers.URLField(help_text="URL of the generated image")
    revised_prompt = serializers.CharField(required=False, help_text="Revised prompt used for generation")