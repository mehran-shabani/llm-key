from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIKeyViewSet, BrowserExtensionAPIKeyViewSet, InviteViewSet

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet)
router.register(r'browser-extension-keys', BrowserExtensionAPIKeyViewSet)
router.register(r'invites', InviteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]