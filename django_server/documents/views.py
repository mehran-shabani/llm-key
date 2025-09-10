from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid

from .models import WorkspaceDocument, DocumentVector, DocumentSyncQueue, DocumentSyncExecution
from .serializers import (
    WorkspaceDocumentSerializer, DocumentVectorSerializer,
    DocumentSyncQueueSerializer, DocumentSyncExecutionSerializer,
    DocumentUploadSerializer, DocumentBulkActionSerializer
)
from workspaces.models import Workspace
from system_settings.models import EventLog, Telemetry


class WorkspaceDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for WorkspaceDocument management."""
    queryset = WorkspaceDocument.objects.all()
    serializer_class = WorkspaceDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """Filter documents based on user's workspace access."""
        user = self.request.user
        if user.role == 'admin':
            queryset = self.queryset
        else:
            # Get workspaces user has access to
            user_workspaces = Workspace.objects.filter(users=user)
            queryset = self.queryset.filter(workspace__in=user_workspaces)
        
        # Filter by workspace if provided
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)
        
        # Filter by pinned/watched status
        pinned = self.request.query_params.get('pinned')
        if pinned is not None:
            queryset = queryset.filter(pinned=pinned.lower() == 'true')
        
        watched = self.request.query_params.get('watched')
        if watched is not None:
            queryset = queryset.filter(watched=watched.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """Upload a document to a workspace."""
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        workspace_id = serializer.validated_data['workspace_id']
        metadata = serializer.validated_data.get('metadata', {})
        
        # Check workspace access
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            if request.user.role != 'admin' and not workspace.users.filter(id=request.user.id).exists():
                return Response(
                    {'error': 'You do not have access to this workspace'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Workspace.DoesNotExist:
            return Response(
                {'error': 'Workspace not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Save file to storage
        doc_id = str(uuid.uuid4())
        file_path = os.path.join('documents', str(workspace_id), file.name)
        saved_path = default_storage.save(file_path, ContentFile(file.read()))
        
        # Create document record
        document = WorkspaceDocument.objects.create(
            doc_id=doc_id,
            filename=file.name,
            docpath=saved_path,
            workspace=workspace,
            metadata=metadata
        )
        
        # Log event
        EventLog.log_event(
            'document_uploaded',
            {
                'filename': file.name,
                'workspace_name': workspace.name,
                'size': file.size
            },
            request.user.id
        )
        
        Telemetry.send_telemetry(
            'document_uploaded',
            {'workspace_id': workspace_id},
            request.user.id
        )
        
        serializer = WorkspaceDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin/unpin a document."""
        document = self.get_object()
        pin = request.data.get('pin', True)
        document.pinned = pin
        document.save()
        
        EventLog.log_event(
            'document_pinned' if pin else 'document_unpinned',
            {'filename': document.filename, 'workspace_name': document.workspace.name},
            request.user.id
        )
        
        return Response({'pinned': document.pinned})
    
    @action(detail=True, methods=['post'])
    def watch(self, request, pk=None):
        """Watch/unwatch a document for changes."""
        document = self.get_object()
        watch = request.data.get('watch', True)
        document.watched = watch
        document.save()
        
        # Add to sync queue if watching
        if watch:
            from django.utils import timezone
            from datetime import timedelta
            
            DocumentSyncQueue.objects.get_or_create(
                workspace_doc=document,
                defaults={
                    'next_sync_at': timezone.now() + timedelta(days=1)
                }
            )
        else:
            # Remove from sync queue if unwatching
            DocumentSyncQueue.objects.filter(workspace_doc=document).delete()
        
        EventLog.log_event(
            'document_watched' if watch else 'document_unwatched',
            {'filename': document.filename, 'workspace_name': document.workspace.name},
            request.user.id
        )
        
        return Response({'watched': document.watched})
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Perform bulk actions on multiple documents."""
        serializer = DocumentBulkActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        document_ids = serializer.validated_data['document_ids']
        action = serializer.validated_data['action']
        
        # Get documents
        documents = self.get_queryset().filter(id__in=document_ids)
        
        if action == 'pin':
            documents.update(pinned=True)
            message = f"Pinned {documents.count()} documents"
        elif action == 'unpin':
            documents.update(pinned=False)
            message = f"Unpinned {documents.count()} documents"
        elif action == 'watch':
            documents.update(watched=True)
            message = f"Watching {documents.count()} documents"
        elif action == 'unwatch':
            documents.update(watched=False)
            message = f"Unwatching {documents.count()} documents"
        elif action == 'delete':
            count = documents.count()
            
            # Delete associated files
            for doc in documents:
                if doc.docpath and default_storage.exists(doc.docpath):
                    default_storage.delete(doc.docpath)
            
            documents.delete()
            message = f"Deleted {count} documents"
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        EventLog.log_event(
            f'documents_bulk_{action}',
            {'count': len(document_ids), 'action': action},
            request.user.id
        )
        
        return Response({'message': message})
    
    def perform_destroy(self, instance):
        """Delete document and associated file."""
        # Delete file from storage
        if instance.docpath and default_storage.exists(instance.docpath):
            default_storage.delete(instance.docpath)
        
        EventLog.log_event(
            'document_deleted',
            {'filename': instance.filename, 'workspace_name': instance.workspace.name},
            self.request.user.id
        )
        
        super().perform_destroy(instance)


class DocumentVectorViewSet(viewsets.ModelViewSet):
    """ViewSet for DocumentVector management."""
    queryset = DocumentVector.objects.all()
    serializer_class = DocumentVectorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by doc_id if provided."""
        queryset = super().get_queryset()
        doc_id = self.request.query_params.get('doc_id')
        if doc_id:
            queryset = queryset.filter(doc_id=doc_id)
        return queryset


class DocumentSyncQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for DocumentSyncQueue management."""
    queryset = DocumentSyncQueue.objects.all()
    serializer_class = DocumentSyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def sync_now(self, request, pk=None):
        """Trigger immediate sync for a document."""
        sync_queue = self.get_object()
        
        # Create sync execution record
        execution = DocumentSyncExecution.objects.create(
            queue=sync_queue,
            status='processing'
        )
        
        # TODO: Trigger actual sync task (would use Celery in production)
        # For now, just mark as success
        execution.status = 'success'
        execution.result = 'Document synced successfully'
        execution.save()
        
        # Update sync queue
        from django.utils import timezone
        from datetime import timedelta
        
        sync_queue.last_synced_at = timezone.now()
        sync_queue.next_sync_at = timezone.now() + timedelta(milliseconds=sync_queue.stale_after_ms)
        sync_queue.save()
        
        EventLog.log_event(
            'document_sync_triggered',
            {'document': sync_queue.workspace_doc.filename},
            request.user.id
        )
        
        return Response({'message': 'Sync triggered successfully', 'execution_id': execution.id})