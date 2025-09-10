from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import AuthResponseSerializer


class AuthView(APIView):
    """
    Verify the attached Authentication header contains a valid API token.
    """
    
    @extend_schema(
        tags=['Authentication'],
        summary='Verify API token',
        description='Verify the attached Authentication header contains a valid API token.',
        responses={
            200: OpenApiResponse(
                response=AuthResponseSerializer,
                description='Valid auth token was found.'
            ),
            403: OpenApiResponse(
                description='Invalid API key'
            )
        }
    )
    def get(self, request):
        """
        Verify API token authentication
        """
        return Response({'authenticated': True}, status=status.HTTP_200_OK)