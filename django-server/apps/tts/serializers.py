from rest_framework import serializers


class TTSRequestSerializer(serializers.Serializer):
    """Serializer for TTS request"""
    text = serializers.CharField(help_text="Text to convert to speech")
    model = serializers.ChoiceField(
        choices=["tts-1", "tts-1-hd"],
        default="tts-1",
        required=False,
        help_text="OpenAI model to use for text-to-speech"
    )
    voice = serializers.ChoiceField(
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        default="alloy",
        required=False,
        help_text="Voice to use for speech synthesis"
    )


class TTSResponseSerializer(serializers.Serializer):
    """Serializer for TTS response"""
    audio_base64 = serializers.CharField(help_text="Base64 encoded audio data")
    model = serializers.CharField(help_text="Model used for speech synthesis")
    voice = serializers.CharField(help_text="Voice used for speech synthesis")