# Feature: Specialized Content Loaders
# Description: Load content from Confluence, YouTube, Obsidian with specialized parsers
# Library: Django, requests, youtube-transcript-api, beautifulsoup4

# 1. models.py - Specialized content sources
from django.db import models
import uuid

class ContentSource(models.Model):
    SOURCE_TYPES = [
        ('confluence', 'Confluence'),
        ('youtube', 'YouTube'),
        ('obsidian', 'Obsidian Vault'),
        ('notion', 'Notion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    name = models.CharField(max_length=200)
    configuration = models.JSONField()  # Source-specific config
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class LoadedContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    source = models.ForeignKey(ContentSource, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=500)
    content = models.TextField()
    source_url = models.URLField()
    author = models.CharField(max_length=200, blank=True)
    word_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

# 2. content_loaders.py - Specialized loader implementations
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
from typing import List, Dict, Any

class BaseContentLoader:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def load_content(self) -> List[Dict[str, Any]]:
        """Load content from source"""
        raise NotImplementedError

class YouTubeTranscriptLoader(BaseContentLoader):
    def __init__(self, config):
        super().__init__(config)
        self.video_url = config.get('video_url')
    
    def extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get video metadata using YouTube API or scraping"""
        try:
            # Simplified: In real implementation, use YouTube Data API v3
            url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info from page
            title_tag = soup.find('meta', property='og:title')
            title = title_tag['content'] if title_tag else f'YouTube Video {video_id}'
            
            description_tag = soup.find('meta', property='og:description')
            description = description_tag['content'] if description_tag else ''
            
            # Try to find channel name
            channel_tag = soup.find('span', {'itemprop': 'author'})
            channel = channel_tag.get_text() if channel_tag else 'Unknown'
            
            return {
                'title': title,
                'description': description,
                'channel': channel,
                'video_id': video_id,
                'url': url
            }
        except Exception as e:
            return {
                'title': f'YouTube Video {video_id}',
                'description': '',
                'channel': 'Unknown',
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
    
    def get_transcript(self, video_id: str) -> str:
        """Get transcript from YouTube video (simplified)"""
        try:
            # In real implementation, use youtube-transcript-api library:
            # from youtube_transcript_api import YouTubeTranscriptApi
            # transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # return ' '.join([entry['text'] for entry in transcript])
            
            # Simplified simulation
            return f"[Simulated transcript for YouTube video {video_id}. In real implementation, this would contain the actual video transcript extracted using youtube-transcript-api library.]"
            
        except Exception as e:
            raise Exception(f"Could not retrieve transcript: {str(e)}")
    
    def load_content(self) -> List[Dict[str, Any]]:
        video_id = self.extract_video_id(self.video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        
        video_info = self.get_video_info(video_id)
        transcript = self.get_transcript(video_id)
        
        return [{
            'title': video_info['title'],
            'content': transcript,
            'source_url': video_info['url'],
            'author': video_info['channel'],
            'word_count': len(transcript.split()),
            'metadata': {
                'video_id': video_id,
                'description': video_info['description'],
                'source_type': 'youtube'
            }
        }]

class ConfluenceLoader(BaseContentLoader):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get('base_url')
        self.space_key = config.get('space_key')
        self.username = config.get('username')
        self.api_token = config.get('api_token')
        self.is_cloud = config.get('is_cloud', True)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Confluence API"""
        if self.is_cloud:
            # Confluence Cloud uses email + API token
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.api_token}".encode()).decode()
            return {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
        else:
            # Confluence Server/Data Center
            return {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
    
    def get_pages_in_space(self) -> List[Dict[str, Any]]:
        """Get all pages in Confluence space"""
        api_url = f"{self.base_url}/rest/api/content"
        headers = self.get_auth_headers()
        
        params = {
            'spaceKey': self.space_key,
            'type': 'page',
            'status': 'current',
            'expand': 'body.storage,metadata,space,history,version',
            'limit': 100
        }
        
        all_pages = []
        start = 0
        
        while True:
            params['start'] = start
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('results', [])
            
            if not pages:
                break
            
            all_pages.extend(pages)
            
            # Check if there are more pages
            if len(pages) < params['limit']:
                break
            
            start += params['limit']
        
        return all_pages
    
    def extract_page_content(self, page_data: Dict[str, Any]) -> str:
        """Extract clean text content from Confluence page"""
        try:
            # Get HTML content from storage format
            html_content = page_data.get('body', {}).get('storage', {}).get('value', '')
            
            if not html_content:
                return ''
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'meta', 'link']):
                element.decompose()
            
            # Get clean text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            return clean_text
            
        except Exception as e:
            print(f"Error extracting content: {str(e)}")
            return ''
    
    def load_content(self) -> List[Dict[str, Any]]:
        pages = self.get_pages_in_space()
        loaded_content = []
        
        for page in pages:
            try:
                content = self.extract_page_content(page)
                if not content:
                    continue
                
                # Build page URL
                page_url = f"{self.base_url}/spaces/{self.space_key}/pages/{page['id']}"
                
                loaded_content.append({
                    'title': page.get('title', 'Untitled'),
                    'content': content,
                    'source_url': page_url,
                    'author': page.get('history', {}).get('createdBy', {}).get('displayName', 'Unknown'),
                    'word_count': len(content.split()),
                    'metadata': {
                        'page_id': page['id'],
                        'space_key': self.space_key,
                        'created_date': page.get('history', {}).get('createdDate'),
                        'last_modified': page.get('version', {}).get('when'),
                        'source_type': 'confluence'
                    }
                })
                
            except Exception as e:
                print(f"Error processing page {page.get('id')}: {str(e)}")
                continue
        
        return loaded_content

class ObsidianVaultLoader(BaseContentLoader):
    def __init__(self, config):
        super().__init__(config)
        self.vault_files = config.get('files', [])  # List of file objects with content
    
    def process_obsidian_links(self, content: str) -> str:
        """Process Obsidian internal links and formatting"""
        # Convert [[link]] to readable format
        content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
        
        # Convert ![[image]] to image reference
        content = re.sub(r'!\[\[([^\]]+)\]\]', r'[Image: \1]', content)
        
        # Convert #tags to readable format
        content = re.sub(r'#([a-zA-Z0-9_-]+)', r'Tag: \1', content)
        
        return content
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter metadata"""
        metadata = {}
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            try:
                end_index = content.find('---', 3)
                if end_index != -1:
                    frontmatter = content[3:end_index].strip()
                    # Simple YAML parsing (in real implementation, use PyYAML)
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()
                    
                    # Remove frontmatter from content
                    content = content[end_index + 3:].strip()
            except Exception:
                pass
        
        return metadata, content
    
    def load_content(self) -> List[Dict[str, Any]]:
        loaded_content = []
        
        for file_data in self.vault_files:
            try:
                file_path = file_data.get('path', '')
                file_name = file_data.get('name', '')
                raw_content = file_data.get('content', '')
                
                if not raw_content or not raw_content.strip():
                    continue
                
                # Extract metadata and clean content
                metadata, content = self.extract_metadata(raw_content)
                
                # Process Obsidian-specific formatting
                processed_content = self.process_obsidian_links(content)
                
                loaded_content.append({
                    'title': metadata.get('title', file_name.replace('.md', '')),
                    'content': processed_content,
                    'source_url': f"obsidian://vault/{file_path}",
                    'author': metadata.get('author', 'Obsidian Vault'),
                    'word_count': len(processed_content.split()),
                    'metadata': {
                        'file_path': file_path,
                        'tags': metadata.get('tags', []),
                        'created': metadata.get('created'),
                        'modified': metadata.get('modified'),
                        'source_type': 'obsidian',
                        **metadata
                    }
                })
                
            except Exception as e:
                print(f"Error processing file {file_data.get('path')}: {str(e)}")
                continue
        
        return loaded_content

# 3. loader_factory.py - Content loader factory
class ContentLoaderFactory:
    @staticmethod
    def create_loader(source_type: str, config: Dict[str, Any]):
        """Create content loader instance"""
        
        if source_type == 'youtube':
            return YouTubeTranscriptLoader(config)
        
        elif source_type == 'confluence':
            return ConfluenceLoader(config)
        
        elif source_type == 'obsidian':
            return ObsidianVaultLoader(config)
        
        else:
            raise ValueError(f"Unsupported content source: {source_type}")

# 4. views.py - Specialized loader API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
import json

@method_decorator(csrf_exempt, name='dispatch')
class LoadSpecializedContentView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            source_type = data.get('source_type')
            config = data.get('config', {})
            source_name = data.get('name', f'{source_type} Source')
            
            if not source_type:
                return JsonResponse({'error': 'Source type is required'}, status=400)
            
            # Create content source record
            content_source = ContentSource.objects.create(
                source_type=source_type,
                name=source_name,
                configuration=config
            )
            
            # Create loader and load content
            loader = ContentLoaderFactory.create_loader(source_type, config)
            loaded_items = loader.load_content()
            
            # Save loaded content
            saved_count = 0
            for item in loaded_items:
                LoadedContent.objects.create(
                    source=content_source,
                    title=item['title'],
                    content=item['content'],
                    source_url=item['source_url'],
                    author=item['author'],
                    word_count=item['word_count'],
                    metadata=item['metadata']
                )
                saved_count += 1
            
            # Update source sync time
            content_source.last_sync = timezone.now()
            content_source.save()
            
            return JsonResponse({
                'success': True,
                'source': {
                    'id': str(content_source.id),
                    'type': content_source.source_type,
                    'name': content_source.name,
                    'items_loaded': saved_count,
                    'last_sync': content_source.last_sync.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ContentSourcesView(View):
    def get(self, request):
        """Get all content sources"""
        try:
            sources = []
            
            for source in ContentSource.objects.filter(is_active=True):
                content_count = source.contents.count()
                total_words = sum(content.word_count for content in source.contents.all())
                
                # Get recent content samples
                recent_content = []
                for content in source.contents.all()[:5]:
                    recent_content.append({
                        'title': content.title,
                        'word_count': content.word_count,
                        'created_at': content.created_at.isoformat(),
                        'preview': content.content[:100] + '...' if len(content.content) > 100 else content.content
                    })
                
                sources.append({
                    'id': str(source.id),
                    'type': source.source_type,
                    'name': source.name,
                    'content_count': content_count,
                    'total_words': total_words,
                    'last_sync': source.last_sync.isoformat() if source.last_sync else None,
                    'recent_content': recent_content
                })
            
            return JsonResponse({'sources': sources})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ContentSourceDetailView(View):
    def get(self, request, source_id):
        """Get detailed information about a content source"""
        try:
            source = ContentSource.objects.get(id=source_id)
            
            contents = []
            for content in source.contents.all():
                contents.append({
                    'id': str(content.id),
                    'title': content.title,
                    'source_url': content.source_url,
                    'author': content.author,
                    'word_count': content.word_count,
                    'created_at': content.created_at.isoformat(),
                    'metadata': content.metadata,
                    'content_preview': content.content[:200] + '...' if len(content.content) > 200 else content.content
                })
            
            return JsonResponse({
                'id': str(source.id),
                'type': source.source_type,
                'name': source.name,
                'configuration': source.configuration,
                'last_sync': source.last_sync.isoformat() if source.last_sync else None,
                'total_content': len(contents),
                'contents': contents
            })
            
        except ContentSource.DoesNotExist:
            return JsonResponse({'error': 'Content source not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import LoadSpecializedContentView, ContentSourcesView, ContentSourceDetailView

urlpatterns = [
    path('content/load/', LoadSpecializedContentView.as_view()),
    path('content/sources/', ContentSourcesView.as_view()),
    path('content/sources/<uuid:source_id>/', ContentSourceDetailView.as_view()),
]