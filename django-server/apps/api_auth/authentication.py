from rest_framework import authentication
from rest_framework import exceptions
from apps.coredb.models import ApiKey


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class for API key validation
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_AUTHORIZATION')
        
        if not api_key:
            return None
            
        # Remove 'Bearer ' prefix if present
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
            
        try:
            api_key_obj = ApiKey.objects.get(secret=api_key)
            return (api_key_obj, None)
        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key')