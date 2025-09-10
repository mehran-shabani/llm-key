"""
URL configuration for AnythingLLM project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# Import views
from authentication.views import CustomTokenObtainPairView, UserViewSet, DesktopMobileDeviceViewSet
from workspaces.views import (
    WorkspaceViewSet, WorkspaceThreadViewSet, WorkspaceSuggestedMessageViewSet,
    SlashCommandPresetViewSet, PromptHistoryViewSet, WorkspaceParsedFileViewSet
)
from documents.views import WorkspaceDocumentViewSet, DocumentVectorViewSet, DocumentSyncQueueViewSet
from chats.views import WorkspaceChatViewSet, WelcomeMessageViewSet

# Create router
router = DefaultRouter()

# Authentication routes
router.register(r'users', UserViewSet)
router.register(r'devices', DesktopMobileDeviceViewSet)

# Workspace routes
router.register(r'workspaces', WorkspaceViewSet)
router.register(r'threads', WorkspaceThreadViewSet)
router.register(r'suggested-messages', WorkspaceSuggestedMessageViewSet)
router.register(r'slash-commands', SlashCommandPresetViewSet)
router.register(r'prompt-history', PromptHistoryViewSet)
router.register(r'parsed-files', WorkspaceParsedFileViewSet)

# Document routes
router.register(r'documents', WorkspaceDocumentViewSet)
router.register(r'document-vectors', DocumentVectorViewSet)
router.register(r'document-sync-queue', DocumentSyncQueueViewSet)

# Chat routes
router.register(r'chats', WorkspaceChatViewSet)
router.register(r'welcome-messages', WelcomeMessageViewSet)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API routes
    path('api/', include(router.urls)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # App-specific URLs
    path('api/embeddings/', include('embeddings.urls')),
    path('api/system/', include('system_settings.urls')),
    path('api/keys/', include('api_keys.urls')),
    
    # Health check
    path('ping/', lambda request: JsonResponse({'online': True}), name='ping'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Import JsonResponse for ping endpoint
from django.http import JsonResponse