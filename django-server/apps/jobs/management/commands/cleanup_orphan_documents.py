import os
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up orphaned files in the direct uploads directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of files to delete in each batch (default: 500)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting files'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        
        try:
            # Get direct uploads path from settings
            direct_uploads_path = getattr(settings, 'DIRECT_UPLOADS_PATH', None)
            if not direct_uploads_path:
                raise CommandError('DIRECT_UPLOADS_PATH not configured in settings')
            
            if not os.path.exists(direct_uploads_path):
                self.stdout.write(
                    self.style.WARNING('No direct uploads path found - exiting.')
                )
                return
            
            # Get list of files in direct uploads directory
            files_in_directory = os.listdir(direct_uploads_path)
            if not files_in_directory:
                self.stdout.write('No files found in direct uploads directory')
                return
            
            # Get known files from database
            # Note: This assumes you have a WorkspaceParsedFiles model
            # You'll need to import and use the appropriate model
            from apps.documents.models import WorkspaceParsedFiles  # Adjust import as needed
            
            known_files = set(
                WorkspaceParsedFiles.objects.values_list('filename', flat=True)
            )
            
            # Find orphaned files
            files_to_delete = []
            for filename in files_in_directory:
                if filename not in known_files:
                    files_to_delete.append(os.path.join(direct_uploads_path, filename))
            
            if not files_to_delete:
                self.stdout.write('No orphaned files found')
                return
            
            self.stdout.write(f'Found {len(files_to_delete)} orphaned files to delete')
            
            if dry_run:
                self.stdout.write('DRY RUN - Files that would be deleted:')
                for file_path in files_to_delete:
                    self.stdout.write(f'  {file_path}')
                return
            
            # Batch delete files
            deleted_count, failed_count = self._batch_delete_files(files_to_delete, batch_size)
            
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {deleted_count} orphaned files')
            )
            if failed_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Failed to delete {failed_count} files')
                )
                
        except Exception as e:
            logger.error(f'Error in cleanup_orphan_documents: {e}')
            raise CommandError(f'Command failed: {e}')

    def _batch_delete_files(self, files_to_delete, batch_size):
        """Delete files in batches"""
        deleted_count = 0
        failed_count = 0
        
        for i in range(0, len(files_to_delete), batch_size):
            batch = files_to_delete[i:i + batch_size]
            
            try:
                # Try batch deletion
                for file_path in batch:
                    try:
                        os.unlink(file_path)
                        deleted_count += 1
                    except OSError as e:
                        failed_count += 1
                        logger.error(f'Failed to delete {file_path}: {e}')
                
                batch_num = (i // batch_size) + 1
                self.stdout.write(f'Deleted batch {batch_num}: {len(batch)} files')
                
            except Exception as e:
                logger.error(f'Batch deletion failed: {e}')
                # If batch fails, try individual files
                for file_path in batch:
                    try:
                        os.unlink(file_path)
                        deleted_count += 1
                    except OSError as e:
                        failed_count += 1
                        logger.error(f'Failed to delete {file_path}: {e}')
        
        return deleted_count, failed_count