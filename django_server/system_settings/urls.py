from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemSettingViewSet, SystemPromptVariableViewSet,
    EventLogViewSet, TelemetryViewSet, CacheDataViewSet,
    SystemStatusView, SetupCompleteView
)

router = DefaultRouter()
router.register(r'settings', SystemSettingViewSet)
router.register(r'prompt-variables', SystemPromptVariableViewSet)
router.register(r'event-logs', EventLogViewSet)
router.register(r'telemetry', TelemetryViewSet)
router.register(r'cache', CacheDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('status/', SystemStatusView.as_view(), name='system-status'),
    path('setup-complete/', SetupCompleteView.as_view(), name='setup-complete'),
]