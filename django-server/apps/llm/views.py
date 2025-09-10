from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import model_registry, openai_client
from .serializers import (
    TextGenerationSerializer,
    TextInstructionSerializer,
    TextGenerationResponseSerializer
)


@api_view(['POST'])
def generate_text(request):
    """
    Generate text using OpenAI chat completions (category: text_gen).
    
    POST /api/llm/generate/
    """
    serializer = TextGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Select model using registry
        model = model_registry.select('text_gen', data.get('model'))
        
        # Prepare parameters for OpenAI API
        params = {
            'model': model,
            'messages': data['messages'],
            'headers': {
                'X-OpenAI-Base-URL': request.headers.get('X-OpenAI-Base-URL'),
                'X-OpenAI-Key': request.headers.get('X-OpenAI-Key')
            }
        }
        
        # Add optional parameters
        if 'temperature' in data:
            params['temperature'] = data['temperature']
        if 'max_tokens' in data:
            params['max_tokens'] = data['max_tokens']
        if 'top_p' in data:
            params['top_p'] = data['top_p']
        if 'frequency_penalty' in data:
            params['frequency_penalty'] = data['frequency_penalty']
        if 'presence_penalty' in data:
            params['presence_penalty'] = data['presence_penalty']
        if 'stop' in data:
            params['stop'] = data['stop']
        
        # Call OpenAI API
        result = openai_client.generate_text(**params)
        
        # Return response
        response_serializer = TextGenerationResponseSerializer(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def instruct_text(request):
    """
    Generate text using OpenAI chat completions for instruction following (category: text2text).
    
    POST /api/llm/instruct/
    """
    serializer = TextInstructionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Select model using registry
        model = model_registry.select('text2text', data.get('model'))
        
        # Prepare parameters for OpenAI API
        params = {
            'model': model,
            'messages': data['messages'],
            'headers': {
                'X-OpenAI-Base-URL': request.headers.get('X-OpenAI-Base-URL'),
                'X-OpenAI-Key': request.headers.get('X-OpenAI-Key')
            }
        }
        
        # Add optional parameters
        if 'temperature' in data:
            params['temperature'] = data['temperature']
        if 'max_tokens' in data:
            params['max_tokens'] = data['max_tokens']
        if 'top_p' in data:
            params['top_p'] = data['top_p']
        if 'frequency_penalty' in data:
            params['frequency_penalty'] = data['frequency_penalty']
        if 'presence_penalty' in data:
            params['presence_penalty'] = data['presence_penalty']
        if 'stop' in data:
            params['stop'] = data['stop']
        
        # Call OpenAI API
        result = openai_client.generate_text(**params)
        
        # Return response
        response_serializer = TextGenerationResponseSerializer(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )