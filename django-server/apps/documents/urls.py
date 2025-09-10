from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document upload endpoints
    path('v1/document/upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('v1/document/upload/<str:folderName>/', views.DocumentUploadFolderView.as_view(), name='document_upload_folder'),
    path('v1/document/upload-link/', views.DocumentUploadLinkView.as_view(), name='document_upload_link'),
    path('v1/document/raw-text/', views.DocumentRawTextView.as_view(), name='document_raw_text'),
    
    # Document listing endpoints
    path('v1/documents/', views.DocumentListView.as_view(), name='document_list'),
    path('v1/documents/folder/<str:folderName>/', views.DocumentFolderView.as_view(), name='document_folder'),
    
    # Document metadata endpoints
    path('v1/document/accepted-file-types/', views.DocumentAcceptedTypesView.as_view(), name='document_accepted_types'),
    path('v1/document/metadata-schema/', views.DocumentMetadataSchemaView.as_view(), name='document_metadata_schema'),
    
    # Document detail endpoint
    path('v1/document/<str:docName>/', views.DocumentDetailView.as_view(), name='document_detail'),
    
    # Document folder management endpoints
    path('v1/document/create-folder/', views.DocumentCreateFolderView.as_view(), name='document_create_folder'),
    path('v1/document/remove-folder/', views.DocumentRemoveFolderView.as_view(), name='document_remove_folder'),
    path('v1/document/move-files/', views.DocumentMoveFilesView.as_view(), name='document_move_files'),
]