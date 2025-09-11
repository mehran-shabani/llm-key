# Feature: Document Sync & Watching
# Description: Automated document synchronization with file change monitoring
# Library: Django, Celery, watchdog, requests

# 1. models.py - Document sync tracking models
from django.db import models
import uuid
from datetime import datetime, timedelta

class WatchedDocument(models.Model):
    SYNC_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    ]
    
    DOCUMENT_TYPES = [
        ('file', 'Local File'),
        ('url', 'Web URL'),
        ('api', 'API Endpoint'),
        ('confluence', 'Confluence Page'),
        ('github', 'GitHub Repository'),
        ('gitlab', 'GitLab Repository'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    source_path = models.CharField(max_length=1000)  # File path, URL, or API endpoint
    title = models.CharField(max_length=500)
    content_hash = models.CharField(max_length=64)  # SHA256 hash for change detection
    sync_interval_hours = models.IntegerField(default=24)  # How often to check for changes
    last_sync = models.DateTimeField(null=True, blank=True)
    next_sync = models.DateTimeField()
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='active')
    failure_count = models.IntegerField(default=0)
    max_failures = models.IntegerField(default=5)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_next_sync(self):
        """Calculate next sync time based on interval"""
        return datetime.now() + timedelta(hours=self.sync_interval_hours)
    
    def is_due_for_sync(self):
        """Check if document is due for sync"""
        return self.next_sync <= datetime.now() and self.sync_status == 'active'
    
    def mark_sync_success(self, new_hash):
        """Mark sync as successful"""
        self.last_sync = datetime.now()
        self.next_sync = self.calculate_next_sync()
        self.content_hash = new_hash
        self.failure_count = 0
        self.sync_status = 'active'
        self.save()
    
    def mark_sync_failure(self, error_message):
        """Mark sync as failed"""
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            self.sync_status = 'failed'
        self.metadata['last_error'] = error_message
        self.metadata['last_error_time'] = datetime.now().isoformat()
        self.save()

class DocumentSyncRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    document = models.ForeignKey(WatchedDocument, on_delete=models.CASCADE, related_name='sync_runs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    success = models.BooleanField(null=True)
    error_message = models.TextField(blank=True)
    changes_detected = models.BooleanField(default=False)
    old_hash = models.CharField(max_length=64, blank=True)
    new_hash = models.CharField(max_length=64, blank=True)
    processing_time_ms = models.IntegerField(null=True)

# 2. document_watchers.py - Document monitoring implementations
import hashlib
import requests
import os
from pathlib import Path
from abc import ABC, abstractmethod
import time

class BaseDocumentWatcher(ABC):
    def __init__(self, watched_doc):
        self.watched_doc = watched_doc
        self.source_path = watched_doc.source_path
        self.metadata = watched_doc.metadata
    
    @abstractmethod
    def fetch_content(self):
        """Fetch current content from source"""
        pass
    
    @abstractmethod
    def extract_metadata(self, content):
        """Extract metadata from content"""
        pass
    
    def calculate_hash(self, content):
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def has_changed(self, content):
        """Check if content has changed since last sync"""
        current_hash = self.calculate_hash(content)
        return current_hash != self.watched_doc.content_hash, current_hash

class FileWatcher(BaseDocumentWatcher):
    def fetch_content(self):
        """Read content from local file"""
        try:
            file_path = Path(self.source_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {self.source_path}")
            
            # Check file modification time
            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'content': content,
                'size': stat.st_size,
                'last_modified': last_modified.isoformat(),
                'file_path': str(file_path.absolute())
            }
            
        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")
    
    def extract_metadata(self, content_data):
        """Extract file metadata"""
        return {
            'file_size': content_data['size'],
            'last_modified': content_data['last_modified'],
            'file_path': content_data['file_path'],
            'line_count': len(content_data['content'].splitlines()),
            'word_count': len(content_data['content'].split())
        }

class URLWatcher(BaseDocumentWatcher):
    def fetch_content(self):
        """Fetch content from web URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Add custom headers from metadata if available
            custom_headers = self.metadata.get('headers', {})
            headers.update(custom_headers)
            
            response = requests.get(
                self.source_path,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Extract text content (simplified)
            from bs4 import BeautifulSoup
            
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                content = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_content = ' '.join(chunk for chunk in chunks if chunk)
                
                title = soup.title.string if soup.title else 'No title'
            else:
                clean_content = response.text
                title = 'Text Content'
            
            return {
                'content': clean_content,
                'title': title,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type'),
                'last_modified': response.headers.get('last-modified'),
                'content_length': len(response.content)
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
    
    def extract_metadata(self, content_data):
        """Extract URL metadata"""
        return {
            'title': content_data['title'],
            'status_code': content_data['status_code'],
            'content_type': content_data['content_type'],
            'last_modified': content_data.get('last_modified'),
            'content_length': content_data['content_length'],
            'word_count': len(content_data['content'].split())
        }

class APIWatcher(BaseDocumentWatcher):
    def fetch_content(self):
        """Fetch content from API endpoint"""
        try:
            api_config = self.metadata.get('api_config', {})
            
            headers = api_config.get('headers', {})
            params = api_config.get('params', {})
            method = api_config.get('method', 'GET').upper()
            
            if method == 'GET':
                response = requests.get(
                    self.source_path,
                    headers=headers,
                    params=params,
                    timeout=30
                )
            elif method == 'POST':
                data = api_config.get('data', {})
                response = requests.post(
                    self.source_path,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=30
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                json_data = response.json()
                content = str(json_data)  # Convert to string for hashing
                
                return {
                    'content': content,
                    'json_data': json_data,
                    'status_code': response.status_code,
                    'response_headers': dict(response.headers)
                }
            except:
                # Fallback to text content
                return {
                    'content': response.text,
                    'status_code': response.status_code,
                    'response_headers': dict(response.headers)
                }
                
        except Exception as e:
            raise Exception(f"Failed to fetch from API: {str(e)}")
    
    def extract_metadata(self, content_data):
        """Extract API metadata"""
        return {
            'status_code': content_data['status_code'],
            'response_headers': content_data['response_headers'],
            'has_json_data': 'json_data' in content_data,
            'content_length': len(content_data['content'])
        }

# 3. sync_service.py - Document synchronization service
class DocumentSyncService:
    @staticmethod
    def create_watcher(watched_doc):
        """Create appropriate watcher for document type"""
        watchers = {
            'file': FileWatcher,
            'url': URLWatcher,
            'api': APIWatcher,
        }
        
        watcher_class = watchers.get(watched_doc.document_type)
        if not watcher_class:
            raise ValueError(f"Unsupported document type: {watched_doc.document_type}")
        
        return watcher_class(watched_doc)
    
    @staticmethod
    def sync_document(watched_doc):
        """Sync a single document"""
        sync_run = DocumentSyncRun.objects.create(
            document=watched_doc,
            old_hash=watched_doc.content_hash
        )
        
        start_time = time.time()
        
        try:
            # Create appropriate watcher
            watcher = DocumentSyncService.create_watcher(watched_doc)
            
            # Fetch current content
            content_data = watcher.fetch_content()
            content = content_data['content']
            
            # Check if content has changed
            has_changed, new_hash = watcher.has_changed(content)
            
            if has_changed:
                # Extract updated metadata
                new_metadata = watcher.extract_metadata(content_data)
                watched_doc.metadata.update(new_metadata)
                
                # Mark sync as successful with changes
                watched_doc.mark_sync_success(new_hash)
                
                sync_run.changes_detected = True
                sync_run.new_hash = new_hash
                sync_run.success = True
                
                print(f"Document {watched_doc.title} has been updated")
                
            else:
                # No changes, just update sync time
                watched_doc.last_sync = datetime.now()
                watched_doc.next_sync = watched_doc.calculate_next_sync()
                watched_doc.save()
                
                sync_run.new_hash = watched_doc.content_hash
                sync_run.success = True
                
                print(f"Document {watched_doc.title} - no changes detected")
            
            processing_time = int((time.time() - start_time) * 1000)
            sync_run.processing_time_ms = processing_time
            sync_run.completed_at = datetime.now()
            sync_run.save()
            
            return {
                'success': True,
                'changes_detected': has_changed,
                'processing_time_ms': processing_time
            }
            
        except Exception as e:
            error_message = str(e)
            
            # Mark document sync as failed
            watched_doc.mark_sync_failure(error_message)
            
            # Update sync run
            sync_run.success = False
            sync_run.error_message = error_message
            sync_run.completed_at = datetime.now()
            sync_run.processing_time_ms = int((time.time() - start_time) * 1000)
            sync_run.save()
            
            print(f"Failed to sync document {watched_doc.title}: {error_message}")
            
            return {
                'success': False,
                'error': error_message,
                'processing_time_ms': sync_run.processing_time_ms
            }
    
    @staticmethod
    def sync_all_due_documents():
        """Sync all documents that are due for synchronization"""
        due_documents = WatchedDocument.objects.filter(
            next_sync__lte=datetime.now(),
            sync_status='active'
        )
        
        results = []
        
        for doc in due_documents:
            print(f"Syncing document: {doc.title}")
            result = DocumentSyncService.sync_document(doc)
            results.append({
                'document_id': str(doc.id),
                'title': doc.title,
                **result
            })
        
        return results

# 4. tasks.py - Celery tasks for background sync
from celery import shared_task

@shared_task
def sync_watched_documents():
    """Celery task to sync all watched documents"""
    try:
        results = DocumentSyncService.sync_all_due_documents()
        
        total_synced = len(results)
        successful_syncs = len([r for r in results if r['success']])
        changes_detected = len([r for r in results if r.get('changes_detected')])
        
        return {
            'total_synced': total_synced,
            'successful_syncs': successful_syncs,
            'changes_detected': changes_detected,
            'results': results
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'total_synced': 0,
            'successful_syncs': 0,
            'changes_detected': 0
        }

@shared_task
def sync_single_document(document_id):
    """Celery task to sync a single document"""
    try:
        watched_doc = WatchedDocument.objects.get(id=document_id)
        result = DocumentSyncService.sync_document(watched_doc)
        
        return {
            'document_id': document_id,
            'title': watched_doc.title,
            **result
        }
        
    except WatchedDocument.DoesNotExist:
        return {
            'error': 'Document not found',
            'document_id': document_id
        }
    except Exception as e:
        return {
            'error': str(e),
            'document_id': document_id
        }

# 5. views.py - Document sync management API
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class WatchDocumentView(View):
    def post(self, request):
        """Add a document to watch list"""
        try:
            data = json.loads(request.body)
            
            document_type = data.get('document_type')
            source_path = data.get('source_path')
            title = data.get('title', source_path)
            sync_interval_hours = data.get('sync_interval_hours', 24)
            metadata = data.get('metadata', {})
            
            if not document_type or not source_path:
                return JsonResponse({
                    'error': 'document_type and source_path are required'
                }, status=400)
            
            # Create initial content hash
            watcher_classes = {
                'file': FileWatcher,
                'url': URLWatcher,
                'api': APIWatcher,
            }
            
            if document_type not in watcher_classes:
                return JsonResponse({
                    'error': f'Unsupported document type: {document_type}'
                }, status=400)
            
            # Create watched document
            watched_doc = WatchedDocument.objects.create(
                document_type=document_type,
                source_path=source_path,
                title=title,
                content_hash='',  # Will be set during first sync
                sync_interval_hours=sync_interval_hours,
                next_sync=datetime.now(),  # Sync immediately
                metadata=metadata
            )
            
            # Trigger initial sync
            from .tasks import sync_single_document
            sync_single_document.delay(str(watched_doc.id))
            
            return JsonResponse({
                'success': True,
                'document': {
                    'id': str(watched_doc.id),
                    'title': watched_doc.title,
                    'document_type': watched_doc.document_type,
                    'source_path': watched_doc.source_path,
                    'sync_interval_hours': watched_doc.sync_interval_hours,
                    'sync_status': watched_doc.sync_status,
                    'next_sync': watched_doc.next_sync.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class WatchedDocumentsView(View):
    def get(self, request):
        """Get all watched documents"""
        try:
            documents = []
            
            for doc in WatchedDocument.objects.all().order_by('-created_at'):
                # Get recent sync runs
                recent_runs = doc.sync_runs.order_by('-started_at')[:5]
                sync_history = []
                
                for run in recent_runs:
                    sync_history.append({
                        'started_at': run.started_at.isoformat(),
                        'success': run.success,
                        'changes_detected': run.changes_detected,
                        'processing_time_ms': run.processing_time_ms,
                        'error_message': run.error_message
                    })
                
                documents.append({
                    'id': str(doc.id),
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'source_path': doc.source_path,
                    'sync_status': doc.sync_status,
                    'sync_interval_hours': doc.sync_interval_hours,
                    'last_sync': doc.last_sync.isoformat() if doc.last_sync else None,
                    'next_sync': doc.next_sync.isoformat(),
                    'failure_count': doc.failure_count,
                    'is_due_for_sync': doc.is_due_for_sync(),
                    'sync_history': sync_history,
                    'metadata': doc.metadata
                })
            
            return JsonResponse({'documents': documents})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 6. urls.py
from django.urls import path
from .views import WatchDocumentView, WatchedDocumentsView

urlpatterns = [
    path('documents/watch/', WatchDocumentView.as_view()),
    path('documents/watched/', WatchedDocumentsView.as_view()),
]