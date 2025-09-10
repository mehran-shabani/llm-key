from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for API endpoints
router = DefaultRouter()

# URL patterns for workspace endpoints
urlpatterns = [
    # Workspace CRUD operations
    path('v1/workspace/new/', views.WorkspaceViewSet.create_workspace, name='workspace-create'),
    path('v1/workspaces/', views.WorkspaceViewSet.list_workspaces, name='workspace-list'),
    path('v1/workspace/<str:slug>/', views.WorkspaceViewSet.get_workspace, name='workspace-detail'),
    path('v1/workspace/<str:slug>/', views.WorkspaceViewSet.delete_workspace, name='workspace-delete'),
    path('v1/workspace/<str:slug>/update/', views.WorkspaceViewSet.update_workspace, name='workspace-update'),
    
    # Workspace chat operations
    path('v1/workspace/<str:slug>/chats/', views.WorkspaceViewSet.get_workspace_chats, name='workspace-chats'),
    path('v1/workspace/<str:slug>/chat/', views.WorkspaceViewSet.chat, name='workspace-chat'),
    path('v1/workspace/<str:slug>/stream-chat/', views.WorkspaceViewSet.stream_chat, name='workspace-stream-chat'),
    
    # Workspace document operations
    path('v1/workspace/<str:slug>/update-embeddings/', views.WorkspaceViewSet.update_embeddings, name='workspace-update-embeddings'),
    path('v1/workspace/<str:slug>/update-pin/', views.WorkspaceViewSet.update_pin, name='workspace-update-pin'),
    
    # Workspace search operations
    path('v1/workspace/<str:slug>/vector-search/', views.WorkspaceViewSet.vector_search, name='workspace-vector-search'),
]