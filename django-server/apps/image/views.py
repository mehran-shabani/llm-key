from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import model_registry, openai_client
from .serializers import ImageGenerationSerializer, ImageGenerationResponseSerializer


@api_view(['POST'])
def generate_image(request):
    """
    Generate image using OpenAI images API (category: image).
    
    POST /api/image/generate/
    """
    serializer = ImageGenerationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    try:
        # Select model using registry
        model = model_registry.select('image', data.get('model'))
        
        # Prepare parameters for OpenAI API
        params = {
            'model': model,
            'prompt': data['prompt'],
            'headers': {
                'X-OpenAI-Base-URL': request.headers.get('X-OpenAI-Base-URL'),
                'X-OpenAI-Key': request.headers.get('X-OpenAI-Key')
            }
        }
        
        # Add optional parameters
        if 'n' in data:
            params['n'] = data['n']
        if 'size' in data:
            params['size'] = data['size']
        if 'quality' in data:
            params['quality'] = data['quality']
        if 'style' in data:
            params['style'] = data['style']
        if 'user' in data:
            params['user'] = data['user']
        
        # Call OpenAI API
        result = openai_client.generate_image(**params)
        
        # Return response
        response_serializer = ImageGenerationResponseSerializer(data=result)
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )