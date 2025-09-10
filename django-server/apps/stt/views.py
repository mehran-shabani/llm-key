import json
import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .serializers import STTRequestSerializer, STTResponseSerializer
from openai import OpenAI


def get_model_config():
    """Get model configuration from MODEL_LIST.MD"""
    model_list_path = os.path.join(settings.BASE_DIR, 'MODEL_LIST.MD')
    try:
        with open(model_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract JSON from markdown
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = content[json_start:json_end]
                config = json.loads(json_str)
                return config.get('stt', {})
    except Exception as e:
        print(f"Error reading model config: {e}")
    
    # Fallback to default
    return {
        "default": "whisper-1",
        "models": ["whisper-1"]
    }


@api_view(['POST'])
@parser_classes([MultiPartParser])
def stt_transcribe(request):
    """
    Transcribe audio to text using OpenAI Whisper
    
    POST /api/stt/
    Content-Type: multipart/form-data
    
    Parameters:
    - audio: Audio file (required)
    - model: Model to use (optional, defaults to whisper-1)
    
    Returns:
    - transcript: Transcribed text
    - model: Model used
    """
    try:
        # Validate request data
        serializer = STTRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        audio_file = serializer.validated_data['audio']
        model = serializer.validated_data.get('model', 'whisper-1')
        
        # Get model configuration
        model_config = get_model_config()
        if model not in model_config.get('models', ['whisper-1']):
            model = model_config.get('default', 'whisper-1')
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Transcribe audio
        audio_file.seek(0)  # Reset file pointer
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text"
        )
        
        # Prepare response
        response_data = {
            'transcript': transcript,
            'model': model
        }
        
        response_serializer = STTResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(
            {'error': f'Transcription failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )