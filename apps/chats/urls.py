from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()

# URL patterns for workspace thread endpoints
urlpatterns = [
    # Workspace thread CRUD operations
    path('v1/workspace/<str:slug>/thread/new/', views.WorkspaceThreadViewSet.create_thread, name='thread-create'),
    path('v1/workspace/<str:slug>/thread/<str:thread_slug>/update/', views.WorkspaceThreadViewSet.update_thread, name='thread-update'),
    path('v1/workspace/<str:slug>/thread/<str:thread_slug>/', views.WorkspaceThreadViewSet.delete_thread, name='thread-delete'),
    
    # Workspace thread chat operations
    path('v1/workspace/<str:slug>/thread/<str:thread_slug>/chats/', views.WorkspaceThreadViewSet.get_thread_chats, name='thread-chats'),
    path('v1/workspace/<str:slug>/thread/<str:thread_slug>/chat/', views.WorkspaceThreadViewSet.chat_with_thread, name='thread-chat'),
    path('v1/workspace/<str:slug>/thread/<str:thread_slug>/stream-chat/', views.WorkspaceThreadViewSet.stream_chat_with_thread, name='thread-stream-chat'),
    
    # Chat management operations
    path('v1/workspace/<str:slug>/update-chat/', views.ChatManagementViewSet.update_chat, name='chat-update'),
    path('v1/workspace/<str:slug>/chat-feedback/<int:chat_id>/', views.ChatManagementViewSet.chat_feedback, name='chat-feedback'),
    path('v1/workspace/<str:slug>/delete-chats/', views.ChatManagementViewSet.delete_chats, name='chat-delete'),
    path('v1/workspace/<str:slug>/delete-edited-chats/', views.ChatManagementViewSet.delete_edited_chats, name='chat-delete-edited'),
    path('v1/workspace/<str:slug>/thread/fork/', views.ChatManagementViewSet.fork_thread, name='thread-fork'),
    path('v1/workspace/workspace-chats/<int:chat_id>/', views.ChatManagementViewSet.hide_chat, name='chat-hide'),
]