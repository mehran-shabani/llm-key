import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync watched documents from various sources (links, YouTube, Confluence, GitHub, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-documents',
            type=int,
            default=None,
            help='Maximum number of documents to process in this run'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually updating documents'
        )

    def handle(self, *args, **options):
        max_documents = options['max_documents']
        dry_run = options['dry_run']
        
        try:
            # Import models - adjust imports based on your Django app structure
            from apps.documents.models import Document, DocumentSyncQueue, DocumentSyncRun
            from apps.workspaces.models import Workspace
            from apps.common.services.collector_api import CollectorApi
            from apps.common.services.vector_db import get_vector_db_class
            from apps.common.services.file_utils import file_data, update_source_document
            
            # Get stale document queues
            queues_to_process = DocumentSyncQueue.get_stale_queues()
            
            if not queues_to_process:
                self.stdout.write('No outstanding documents to sync. Exiting.')
                return
            
            # Limit documents if specified
            if max_documents:
                queues_to_process = queues_to_process[:max_documents]
            
            # Check collector API availability
            collector = CollectorApi()
            if not collector.is_online():
                self.stdout.write(
                    self.style.WARNING('Could not reach collector API. Exiting.')
                )
                return
            
            self.stdout.write(
                f'{len(queues_to_process)} watched documents have been found to be stale and will be updated now.'
            )
            
            processed_count = 0
            success_count = 0
            failed_count = 0
            
            for queue in queues_to_process:
                try:
                    result = self._process_document_queue(queue, collector, dry_run)
                    processed_count += 1
                    
                    if result['success']:
                        success_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f'Error processing queue {queue.id}: {e}')
                    failed_count += 1
                    processed_count += 1
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {processed_count} documents: '
                    f'{success_count} successful, {failed_count} failed'
                )
            )
            
        except Exception as e:
            logger.error(f'Error in sync_watched_documents: {e}')
            raise CommandError(f'Command failed: {e}')

    def _process_document_queue(self, queue, collector, dry_run=False):
        """Process a single document queue"""
        from apps.documents.models import Document, DocumentSyncQueue, DocumentSyncRun
        from apps.common.services.vector_db import get_vector_db_class
        from apps.common.services.file_utils import file_data, update_source_document
        
        document = queue.workspace_doc
        workspace = document.workspace
        metadata, doc_type, source = Document.parse_document_type_and_source(document)
        
        # Validate document
        if not metadata or doc_type not in DocumentSyncQueue.VALID_FILE_TYPES:
            self.stdout.write(
                f'Document {document.filename} has no metadata, is broken, or invalid and has been removed from all future runs.'
            )
            if not dry_run:
                DocumentSyncQueue.unwatch(document)
            return {'success': False, 'reason': 'Invalid document'}
        
        # Get new content based on document type
        new_content = None
        
        if doc_type in ['link', 'youtube']:
            response = collector.forward_extension_request(
                endpoint="/ext/resync-source-document",
                method="POST",
                body={
                    'type': doc_type,
                    'options': {'link': source}
                }
            )
            new_content = response.get('content') if response else None
            
        elif doc_type in ['confluence', 'github', 'gitlab', 'drupalwiki']:
            response = collector.forward_extension_request(
                endpoint="/ext/resync-source-document",
                method="POST",
                body={
                    'type': doc_type,
                    'options': {'chunkSource': metadata.get('chunkSource')}
                }
            )
            new_content = response.get('content') if response else None
        
        if not new_content:
            # Check for repeated failures
            failed_run_count = DocumentSyncRun.objects.filter(
                queue_id=queue.id,
                status=DocumentSyncRun.STATUS_FAILED
            ).count()
            
            if failed_run_count >= DocumentSyncQueue.MAX_REPEAT_FAILURES:
                self.stdout.write(
                    f'Document {document.filename} has failed to refresh {failed_run_count} times continuously and will now be removed from the watched document set.'
                )
                if not dry_run:
                    DocumentSyncQueue.unwatch(document)
                return {'success': False, 'reason': 'Too many failures'}
            
            self.stdout.write(
                f'Failed to get new content from collector for source {source}. '
                f'Skipping, but will retry next worker interval. '
                f'Attempt {failed_run_count + 1}/{DocumentSyncQueue.MAX_REPEAT_FAILURES}'
            )
            
            if not dry_run:
                DocumentSyncQueue.save_run(
                    queue.id, 
                    DocumentSyncRun.STATUS_FAILED, 
                    {
                        'filename': document.filename, 
                        'workspacesModified': [], 
                        'reason': 'No content found.'
                    }
                )
            
            return {'success': False, 'reason': 'No content found'}
        
        # Check if content has changed
        current_document_data = file_data(document.docpath)
        if current_document_data.get('pageContent') == new_content:
            next_sync = DocumentSyncQueue.calc_next_sync(queue)
            self.stdout.write(
                f'Source {source} is unchanged and will be skipped. '
                f'Next sync will be {next_sync.strftime("%Y-%m-%d %H:%M:%S")}.'
            )
            
            if not dry_run:
                DocumentSyncQueue.update_queue(
                    queue.id,
                    {
                        'last_synced_at': timezone.now(),
                        'next_sync_at': next_sync,
                    }
                )
                DocumentSyncQueue.save_run(
                    queue.id, 
                    DocumentSyncRun.STATUS_EXITED, 
                    {
                        'filename': document.filename, 
                        'workspacesModified': [], 
                        'reason': 'Content unchanged.'
                    }
                )
            
            return {'success': True, 'reason': 'Content unchanged'}
        
        if dry_run:
            self.stdout.write(f'Would update document {document.filename} with new content')
            return {'success': True, 'reason': 'Dry run'}
        
        # Update document and vector database
        vector_database = get_vector_db_class()
        
        # Delete old document from vector DB
        vector_database.delete_document_from_namespace(workspace.slug, document.doc_id)
        
        # Add updated document to vector DB
        updated_document_data = {
            **current_document_data,
            'pageContent': new_content,
            'docId': document.doc_id,
        }
        
        vector_database.add_document_to_namespace(
            workspace.slug,
            updated_document_data,
            document.docpath,
            skip_cache=True
        )
        
        # Update source document file
        update_source_document(
            document.docpath,
            {
                **updated_document_data,
                'published': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
        )
        
        self.stdout.write(
            f'Workspace "{workspace.name}" vectors of {source} updated. '
            'Document and vector cache updated.'
        )
        
        # Update other workspaces that reference this document
        workspaces_modified = [workspace.slug]
        additional_references = Document.objects.filter(
            filename=document.filename
        ).exclude(id=document.id).select_related('workspace')
        
        if additional_references.exists():
            self.stdout.write(
                f'{source} is referenced in {additional_references.count()} other workspaces. '
                'Updating those workspaces as well...'
            )
            
            for additional_doc in additional_references:
                additional_workspace = additional_doc.workspace
                workspaces_modified.append(additional_workspace.slug)
                
                vector_database.delete_document_from_namespace(
                    additional_workspace.slug, 
                    additional_doc.doc_id
                )
                vector_database.add_document_to_namespace(
                    additional_workspace.slug,
                    updated_document_data,
                    additional_doc.docpath,
                )
                
                self.stdout.write(
                    f'Workspace "{additional_workspace.name}" vectors for {source} '
                    'was also updated with the new content from cache.'
                )
        
        # Update queue for next sync
        next_refresh = DocumentSyncQueue.calc_next_sync(queue)
        self.stdout.write(
            f'{source} has been refreshed in all workspaces it is currently referenced in. '
            f'Next refresh will be {next_refresh.strftime("%Y-%m-%d %H:%M:%S")}.'
        )
        
        DocumentSyncQueue.update_queue(
            queue.id,
            {
                'last_synced_at': timezone.now(),
                'next_sync_at': next_refresh,
            }
        )
        
        DocumentSyncQueue.save_run(
            queue.id, 
            DocumentSyncRun.STATUS_SUCCESS, 
            {
                'filename': document.filename, 
                'workspacesModified': workspaces_modified
            }
        )
        
        return {'success': True, 'reason': 'Updated successfully'}