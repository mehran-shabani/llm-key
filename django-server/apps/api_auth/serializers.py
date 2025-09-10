from rest_framework import serializers


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication response"""
    authenticated = serializers.BooleanField()