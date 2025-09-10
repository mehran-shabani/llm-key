"""
URL configuration for API schema endpoints
"""
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

app_name = 'api_schema'

urlpatterns = [
    # OpenAPI schema endpoint
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI endpoint
    path('docs/', SpectacularSwaggerView.as_view(url_name='api_schema:schema'), name='swagger-ui'),
    
    # ReDoc endpoint (alternative documentation)
    path('redoc/', SpectacularRedocView.as_view(url_name='api_schema:schema'), name='redoc'),
]