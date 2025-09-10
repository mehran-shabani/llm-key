from django.urls import path
from . import views

app_name = 'api_system'

urlpatterns = [
    path('env-dump', views.EnvDumpView.as_view(), name='env-dump'),
    path('', views.SystemSettingsView.as_view(), name='settings'),
    path('vector-count', views.VectorCountView.as_view(), name='vector-count'),
    path('update-env', views.UpdateEnvView.as_view(), name='update-env'),
    path('export-chats', views.ExportChatsView.as_view(), name='export-chats'),
    path('remove-documents', views.RemoveDocumentsView.as_view(), name='remove-documents'),
]