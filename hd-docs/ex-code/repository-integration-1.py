# Feature: Repository Integration
# Description: Integrate with GitHub and GitLab repositories to process code files
# Library: Django, requests, PyGithub, python-gitlab

# 1. models.py - Repository integration models
from django.db import models
import uuid

class RepositorySource(models.Model):
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    repository_url = models.URLField()
    author = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default='main')
    access_token = models.CharField(max_length=200, blank=True)  # Encrypted in real app
    ignore_paths = models.JSONField(default=list)  # Paths to ignore
    total_files = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RepositoryFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    repository = models.ForeignKey(RepositorySource, on_delete=models.CASCADE, related_name='files')
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=200)
    file_type = models.CharField(max_length=20)
    content = models.TextField()
    size_bytes = models.IntegerField()
    line_count = models.IntegerField()
    language = models.CharField(max_length=50, blank=True)
    sha_hash = models.CharField(max_length=40, blank=True)  # Git SHA
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('repository', 'file_path')

# 2. repository_loaders.py - Repository integration logic
import requests
import base64
from urllib.parse import urlparse
import os
import re

class BaseRepositoryLoader:
    
    # Common file types to process
    SUPPORTED_FILE_TYPES = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.md': 'markdown',
        '.txt': 'text',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sql': 'sql',
        '.sh': 'bash',
        '.dockerfile': 'docker',
        '.r': 'r',
        '.m': 'matlab',
    }
    
    # Files/directories to ignore by default
    DEFAULT_IGNORE_PATTERNS = [
        '.git', '.gitignore', 'node_modules', '__pycache__', '.venv', 'venv',
        '.env', '.DS_Store', 'Thumbs.db', '*.log', '*.tmp', '*.cache',
        'dist', 'build', 'target', 'out', '.idea', '.vscode'
    ]
    
    def __init__(self, repository_url, branch='main', access_token=None, ignore_paths=None):
        self.repository_url = repository_url.rstrip('/')
        if self.repository_url.endswith('.git'):
            self.repository_url = self.repository_url[:-4]
        
        self.branch = branch
        self.access_token = access_token
        self.ignore_paths = ignore_paths or []
        self.ignore_patterns = self.DEFAULT_IGNORE_PATTERNS + self.ignore_paths
        
        # Parse repository info
        self.author, self.project_name = self._parse_repo_url()
    
    def _parse_repo_url(self):
        """Parse repository URL to extract author and project name"""
        parsed = urlparse(self.repository_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]
        else:
            raise ValueError(f"Invalid repository URL: {self.repository_url}")
    
    def _should_ignore_file(self, file_path):
        """Check if file should be ignored based on patterns"""
        file_name = os.path.basename(file_path)
        
        for pattern in self.ignore_patterns:
            if pattern in file_path or file_name.startswith('.'):
                return True
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        return ext.lower() not in self.SUPPORTED_FILE_TYPES
    
    def _get_file_language(self, file_path):
        """Determine programming language from file extension"""
        _, ext = os.path.splitext(file_path)
        return self.SUPPORTED_FILE_TYPES.get(ext.lower(), 'unknown')

class GitHubRepositoryLoader(BaseRepositoryLoader):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_base = 'https://api.github.com'
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Repository-Loader/1.0'
        }
        
        if self.access_token:
            self.headers['Authorization'] = f'token {self.access_token}'
    
    def get_repository_info(self):
        """Get basic repository information"""
        url = f"{self.api_base}/repos/{self.author}/{self.project_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                'success': True,
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', ''),
                'default_branch': repo_data['default_branch'],
                'language': repo_data.get('language'),
                'size': repo_data['size'],
                'private': repo_data['private']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_repository_files(self, path=''):
        """Recursively list all files in repository"""
        url = f"{self.api_base}/repos/{self.author}/{self.project_name}/contents/{path}"
        params = {'ref': self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            items = response.json()
            files = []
            
            for item in items:
                if item['type'] == 'file':
                    if not self._should_ignore_file(item['path']):
                        files.append({
                            'path': item['path'],
                            'name': item['name'],
                            'size': item['size'],
                            'sha': item['sha'],
                            'download_url': item['download_url']
                        })
                elif item['type'] == 'dir':
                    # Recursively get files from subdirectory
                    if not self._should_ignore_file(item['path']):
                        subdir_files = self.list_repository_files(item['path'])
                        files.extend(subdir_files)
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def get_file_content(self, file_path):
        """Get content of a specific file"""
        url = f"{self.api_base}/repos/{self.author}/{self.project_name}/contents/{file_path}"
        params = {'ref': self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            file_data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
            
            return {
                'success': True,
                'content': content,
                'size': file_data['size'],
                'sha': file_data['sha'],
                'encoding': file_data['encoding']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class GitLabRepositoryLoader(BaseRepositoryLoader):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Determine if this is GitLab.com or self-hosted
        parsed_url = urlparse(self.repository_url)
        self.gitlab_host = f"{parsed_url.scheme}://{parsed_url.netloc}"
        self.api_base = f"{self.gitlab_host}/api/v4"
        
        self.headers = {
            'User-Agent': 'Repository-Loader/1.0'
        }
        
        if self.access_token:
            self.headers['Private-Token'] = self.access_token
    
    def get_repository_info(self):
        """Get basic repository information"""
        project_path = f"{self.author}/{self.project_name}"
        url = f"{self.api_base}/projects/{requests.utils.quote(project_path, safe='')}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                'success': True,
                'name': repo_data['name'],
                'full_name': repo_data['name_with_namespace'],
                'description': repo_data.get('description', ''),
                'default_branch': repo_data['default_branch'],
                'language': None,  # GitLab doesn't provide this in basic info
                'size': None,
                'private': repo_data['visibility'] == 'private'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_repository_files(self, path=''):
        """List all files in repository using GitLab API"""
        project_path = f"{self.author}/{self.project_name}"
        url = f"{self.api_base}/projects/{requests.utils.quote(project_path, safe='')}/repository/tree"
        params = {
            'ref': self.branch,
            'recursive': True,
            'per_page': 100
        }
        
        try:
            files = []
            page = 1
            
            while True:
                params['page'] = page
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                
                items = response.json()
                if not items:
                    break
                
                for item in items:
                    if item['type'] == 'blob':  # File
                        if not self._should_ignore_file(item['path']):
                            files.append({
                                'path': item['path'],
                                'name': item['name'],
                                'id': item['id']
                            })
                
                # Check if there are more pages
                if len(items) < params['per_page']:
                    break
                page += 1
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def get_file_content(self, file_path):
        """Get content of a specific file"""
        project_path = f"{self.author}/{self.project_name}"
        url = f"{self.api_base}/projects/{requests.utils.quote(project_path, safe='')}/repository/files/{requests.utils.quote(file_path, safe='')}"
        params = {'ref': self.branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            file_data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
            
            return {
                'success': True,
                'content': content,
                'size': file_data['size'],
                'sha': file_data.get('commit_id', ''),
                'encoding': file_data['encoding']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# 3. views.py - Repository integration API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
import threading

@method_decorator(csrf_exempt, name='dispatch')
class RepositoryIntegrationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            repository_url = data.get('repository_url')
            platform = data.get('platform', 'github')
            branch = data.get('branch', 'main')
            access_token = data.get('access_token', '')
            ignore_paths = data.get('ignore_paths', [])
            
            if not repository_url:
                return JsonResponse({'error': 'Repository URL is required'}, status=400)
            
            # Create repository source record
            if platform == 'github':
                loader = GitHubRepositoryLoader(
                    repository_url, branch, access_token, ignore_paths
                )
            elif platform == 'gitlab':
                loader = GitLabRepositoryLoader(
                    repository_url, branch, access_token, ignore_paths
                )
            else:
                return JsonResponse({'error': 'Unsupported platform'}, status=400)
            
            # Get repository info first
            repo_info = loader.get_repository_info()
            if not repo_info['success']:
                return JsonResponse({'error': repo_info['error']}, status=400)
            
            # Create repository record
            repository = RepositorySource.objects.create(
                platform=platform,
                repository_url=repository_url,
                author=loader.author,
                project_name=loader.project_name,
                branch=branch,
                access_token=access_token,  # In production, encrypt this
                ignore_paths=ignore_paths,
                status='pending'
            )
            
            # Start processing in background
            processing_thread = threading.Thread(
                target=self._process_repository,
                args=(repository.id, loader)
            )
            processing_thread.start()
            
            return JsonResponse({
                'success': True,
                'repository': {
                    'id': str(repository.id),
                    'platform': repository.platform,
                    'repository_url': repository.repository_url,
                    'author': repository.author,
                    'project_name': repository.project_name,
                    'branch': repository.branch,
                    'status': repository.status,
                    'repo_info': repo_info
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _process_repository(self, repository_id, loader):
        """Process repository files in background"""
        try:
            repository = RepositorySource.objects.get(id=repository_id)
            repository.status = 'processing'
            repository.save()
            
            # Get all files
            files = loader.list_repository_files()
            repository.total_files = len(files)
            repository.save()
            
            processed_count = 0
            total_lines = 0
            
            for file_info in files:
                try:
                    # Get file content
                    content_result = loader.get_file_content(file_info['path'])
                    
                    if content_result['success']:
                        content = content_result['content']
                        line_count = len(content.splitlines())
                        
                        # Save file to database
                        RepositoryFile.objects.update_or_create(
                            repository=repository,
                            file_path=file_info['path'],
                            defaults={
                                'file_name': file_info['name'],
                                'file_type': os.path.splitext(file_info['name'])[1],
                                'content': content,
                                'size_bytes': content_result['size'],
                                'line_count': line_count,
                                'language': loader._get_file_language(file_info['path']),
                                'sha_hash': content_result.get('sha', '')
                            }
                        )
                        
                        processed_count += 1
                        total_lines += line_count
                        
                        # Update progress
                        repository.processed_files = processed_count
                        repository.total_lines = total_lines
                        repository.save()
                
                except Exception as e:
                    print(f"Error processing file {file_info['path']}: {str(e)}")
                    continue
            
            # Mark as completed
            repository.status = 'completed'
            repository.save()
            
        except Exception as e:
            repository = RepositorySource.objects.get(id=repository_id)
            repository.status = 'failed'
            repository.error_message = str(e)
            repository.save()

class RepositoryStatusView(View):
    def get(self, request, repository_id):
        try:
            repository = RepositorySource.objects.get(id=repository_id)
            
            # Get sample files
            sample_files = []
            for file_obj in repository.files.all()[:10]:
                sample_files.append({
                    'path': file_obj.file_path,
                    'name': file_obj.file_name,
                    'language': file_obj.language,
                    'line_count': file_obj.line_count,
                    'size_bytes': file_obj.size_bytes,
                    'content_preview': file_obj.content[:200] + '...' if len(file_obj.content) > 200 else file_obj.content
                })
            
            return JsonResponse({
                'id': str(repository.id),
                'platform': repository.platform,
                'repository_url': repository.repository_url,
                'author': repository.author,
                'project_name': repository.project_name,
                'branch': repository.branch,
                'status': repository.status,
                'total_files': repository.total_files,
                'processed_files': repository.processed_files,
                'total_lines': repository.total_lines,
                'error_message': repository.error_message,
                'created_at': repository.created_at.isoformat(),
                'sample_files': sample_files
            })
            
        except RepositorySource.DoesNotExist:
            return JsonResponse({'error': 'Repository not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 4. urls.py
from django.urls import path
from .views import RepositoryIntegrationView, RepositoryStatusView

urlpatterns = [
    path('repository/integrate/', RepositoryIntegrationView.as_view()),
    path('repository/<uuid:repository_id>/status/', RepositoryStatusView.as_view()),
]