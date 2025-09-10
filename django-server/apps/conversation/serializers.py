from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


class ConversationRequestSerializer(serializers.Serializer):
    """Serializer for conversation request"""
    audio = serializers.FileField(required=True)
    stt_model = serializers.CharField(required=False, allow_blank=True)
    text_model = serializers.CharField(required=False, allow_blank=True)
    tts_model = serializers.CharField(required=False, allow_blank=True)
    
    def validate_audio(self, value):
        """Validate audio file"""
        if not isinstance(value, (InMemoryUploadedFile, TemporaryUploadedFile)):
            raise serializers.ValidationError("Invalid audio file format")
        
        # Check file size (max 25MB for OpenAI Whisper)
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError("Audio file too large. Maximum size is 25MB.")
        
        # Check file extension
        allowed_extensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        file_extension = value.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported audio format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        return value


class ConversationResponseSerializer(serializers.Serializer):
    """Serializer for conversation response"""
    transcript = serializers.CharField()
    text_response = serializers.CharField()
    audio = serializers.CharField()  # base64 encoded audio
    models_used = serializers.DictField()
    success = serializers.BooleanField()
    errors = serializers.ListField(child=serializers.CharField(), required=False)