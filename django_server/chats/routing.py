from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<workspace_slug>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/agent/(?P<workspace_slug>\w+)/$', consumers.AgentConsumer.as_asgi()),
]