from rest_framework import serializers


class STTRequestSerializer(serializers.Serializer):
    """Serializer for STT request"""
    audio = serializers.FileField(help_text="Audio file to transcribe")
    model = serializers.ChoiceField(
        choices=["whisper-1"],
        default="whisper-1",
        required=False,
        help_text="OpenAI model to use for transcription"
    )


class STTResponseSerializer(serializers.Serializer):
    """Serializer for STT response"""
    transcript = serializers.CharField(help_text="Transcribed text from audio")
    model = serializers.CharField(help_text="Model used for transcription")