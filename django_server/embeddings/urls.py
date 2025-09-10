from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmbedConfigViewSet, EmbedChatViewSet

router = DefaultRouter()
router.register(r'configs', EmbedConfigViewSet)
router.register(r'chats', EmbedChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]