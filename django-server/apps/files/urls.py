from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # File upload endpoints
    path('v1/files/upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('v1/files/assets/upload/', views.AssetUploadView.as_view(), name='asset_upload'),
    path('v1/files/pfp/upload/', views.ProfilePictureUploadView.as_view(), name='pfp_upload'),
    
    # File management endpoints
    path('v1/files/', views.FileListView.as_view(), name='file_list'),
    path('v1/files/<str:filename>/', views.FileDetailView.as_view(), name='file_detail'),
    path('v1/files/<str:filename>/delete/', views.FileDeleteView.as_view(), name='file_delete'),
    path('v1/files/move/', views.FileMoveView.as_view(), name='file_move'),
    
    # Storage information endpoint
    path('v1/files/storage-info/', views.StorageInfoView.as_view(), name='storage_info'),
]