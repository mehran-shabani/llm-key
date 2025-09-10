import os
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import JsonResponse
from django.conf import settings
import logging

from .serializers import ConversationRequestSerializer, ConversationResponseSerializer
from .services import ConversationService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def conversation_view(request):
    """
    POST /api/conversation/
    
    Process voice conversation: STT → LLM → TTS
    
    Input:
    - audio: multipart file (required)
    - stt_model: optional string
    - text_model: optional string  
    - tts_model: optional string
    
    Output:
    - transcript: string
    - text_response: string
    - audio: base64 string
    - models_used: dict
    """
    try:
        # Validate request data
        serializer = ConversationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get OpenAI credentials from headers or environment
        api_key = None
        base_url = None
        
        # Try to get from headers first
        if 'X-OpenAI-API-Key' in request.headers:
            api_key = request.headers['X-OpenAI-API-Key']
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        
        # Try to get from environment variables
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return Response(
                {"error": "OpenAI API key not provided. Set X-OpenAI-API-Key header or OPENAI_API_KEY environment variable."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get base URL from headers or environment
        if 'X-OpenAI-Base-URL' in request.headers:
            base_url = request.headers['X-OpenAI-Base-URL']
        else:
            base_url = os.getenv('OPENAI_BASE_URL')
        
        # Initialize conversation service
        conversation_service = ConversationService(api_key, base_url)
        
        # Process the conversation
        audio_file = serializer.validated_data['audio']
        stt_model = serializer.validated_data.get('stt_model') or None
        text_model = serializer.validated_data.get('text_model') or None
        tts_model = serializer.validated_data.get('tts_model') or None
        
        result = conversation_service.process_conversation(
            audio_file=audio_file,
            stt_model=stt_model,
            text_model=text_model,
            tts_model=tts_model
        )
        
        # Validate response
        response_serializer = ConversationResponseSerializer(data=result)
        if not response_serializer.is_valid():
            logger.error(f"Invalid response data: {response_serializer.errors}")
            return Response(
                {"error": "Internal processing error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return success or partial success
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            # Return partial results with errors
            return Response(result, status=status.HTTP_206_PARTIAL_CONTENT)
            
    except Exception as e:
        logger.error(f"Unexpected error in conversation view: {str(e)}")
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )