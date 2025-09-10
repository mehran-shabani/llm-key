import base64
import json
import os
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TTSRequestSerializer, TTSResponseSerializer
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
                return config.get('tts', {})
    except Exception as e:
        print(f"Error reading model config: {e}")
    
    # Fallback to default
    return {
        "default": "tts-1",
        "models": ["tts-1", "tts-1-hd"]
    }


@api_view(['POST'])
def tts_synthesize(request):
    """
    Convert text to speech using OpenAI TTS
    
    POST /api/tts/
    Content-Type: application/json
    
    Parameters:
    - text: Text to convert to speech (required)
    - model: Model to use (optional, defaults to tts-1)
    - voice: Voice to use (optional, defaults to alloy)
    
    Returns:
    - audio_base64: Base64 encoded audio data
    - model: Model used
    - voice: Voice used
    """
    try:
        # Validate request data
        serializer = TTSRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text = serializer.validated_data['text']
        model = serializer.validated_data.get('model', 'tts-1')
        voice = serializer.validated_data.get('voice', 'alloy')
        
        # Get model configuration
        model_config = get_model_config()
        if model not in model_config.get('models', ['tts-1', 'tts-1-hd']):
            model = model_config.get('default', 'tts-1')
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Generate speech
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        # Convert audio to base64
        audio_data = response.content
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Prepare response
        response_data = {
            'audio_base64': audio_base64,
            'model': model,
            'voice': voice
        }
        
        response_serializer = TTSResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(
            {'error': f'Speech synthesis failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )