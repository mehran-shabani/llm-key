# Feature: Web Content Extraction
# Description: Scrape and process web content with configurable depth crawling
# Library: Django, requests, beautifulsoup4, selenium

# 1. models.py - Web scraping results storage
from django.db import models
import uuid
from urllib.parse import urlparse

class ScrapedWebsite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    start_url = models.URLField()
    domain = models.CharField(max_length=200)
    max_depth = models.IntegerField(default=1)
    max_pages = models.IntegerField(default=20)
    pages_scraped = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class ScrapedPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    website = models.ForeignKey(ScrapedWebsite, on_delete=models.CASCADE, related_name='pages')
    url = models.URLField()
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    word_count = models.IntegerField(default=0)
    depth_level = models.IntegerField(default=0)
    scrape_duration_ms = models.IntegerField(default=0)
    content_type = models.CharField(max_length=50, default='text/html')
    status_code = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('website', 'url')

# 2. web_scraper.py - Web scraping logic
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class WebContentExtractor:
    
    def __init__(self, max_depth=1, max_pages=20, respect_robots=True, use_selenium=False):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if self.use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def can_fetch(self, url):
        """Check if we can fetch the URL according to robots.txt"""
        if not self.respect_robots:
            return True
        
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            return rp.can_fetch(self.session.headers.get('User-Agent', '*'), url)
        except Exception:
            return True  # If we can't check robots.txt, assume it's okay
    
    def extract_links(self, html_content, base_url):
        """Extract links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            # Only include links from the same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                # Clean up the URL (remove fragments, query params if needed)
                parsed = urlparse(absolute_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                links.add(clean_url)
        
        return list(links)
    
    def scrape_page_content(self, url):
        """Scrape content from a single page"""
        start_time = time.time()
        
        try:
            if not self.can_fetch(url):
                return {
                    'success': False,
                    'error': 'Blocked by robots.txt',
                    'status_code': None
                }
            
            if self.use_selenium:
                content_data = self._scrape_with_selenium(url)
            else:
                content_data = self._scrape_with_requests(url)
            
            if content_data['success']:
                # Extract clean text content
                soup = BeautifulSoup(content_data['html'], 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else ''
                
                # Get main content
                # Try to find main content areas first
                main_content = (
                    soup.find('main') or 
                    soup.find('article') or 
                    soup.find('div', class_=re.compile(r'content|main|body', re.I)) or
                    soup.find('body')
                )
                
                if main_content:
                    text_content = main_content.get_text()
                else:
                    text_content = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = ' '.join(chunk for chunk in chunks if chunk)
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return {
                    'success': True,
                    'title': title,
                    'content': clean_text,
                    'html': content_data['html'],
                    'word_count': len(clean_text.split()) if clean_text else 0,
                    'status_code': content_data.get('status_code', 200),
                    'processing_time_ms': processing_time,
                    'content_type': content_data.get('content_type', 'text/html')
                }
            else:
                return content_data
                
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': processing_time
            }
    
    def _scrape_with_requests(self, url):
        """Scrape using requests library"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'html': response.text,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', 'text/html')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def _scrape_with_selenium(self, url):
        """Scrape using Selenium for JavaScript-heavy sites"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source after JavaScript execution
            html = self.driver.page_source
            
            return {
                'success': True,
                'html': html,
                'status_code': 200,  # Selenium doesn't provide status codes directly
                'content_type': 'text/html'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def discover_links(self, start_url):
        """Discover links with depth-first crawling"""
        discovered_links = set([start_url])
        queue = [(start_url, 0)]  # (url, depth)
        
        while queue and len(discovered_links) < self.max_pages:
            current_url, current_depth = queue.pop(0)
            
            if current_depth >= self.max_depth:
                continue
            
            # Scrape current page to get links
            result = self.scrape_page_content(current_url)
            if result['success']:
                links = self.extract_links(result['html'], current_url)
                
                for link in links:
                    if link not in discovered_links and len(discovered_links) < self.max_pages:
                        discovered_links.add(link)
                        if current_depth + 1 < self.max_depth:
                            queue.append((link, current_depth + 1))
        
        return list(discovered_links)
    
    def cleanup(self):
        """Clean up resources"""
        if self.use_selenium and hasattr(self, 'driver'):
            self.driver.quit()

# 3. views.py - Web scraping API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
import json
import threading

@method_decorator(csrf_exempt, name='dispatch')
class WebScrapingView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            start_url = data.get('url')
            max_depth = int(data.get('max_depth', 1))
            max_pages = int(data.get('max_pages', 20))
            use_selenium = data.get('use_selenium', False)
            
            if not start_url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # Validate URL
            from urllib.parse import urlparse
            parsed = urlparse(start_url)
            if not parsed.scheme or not parsed.netloc:
                return JsonResponse({'error': 'Invalid URL format'}, status=400)
            
            # Create scraping job
            website = ScrapedWebsite.objects.create(
                start_url=start_url,
                domain=parsed.netloc,
                max_depth=max_depth,
                max_pages=max_pages,
                status='pending'
            )
            
            # Start scraping in background thread
            scraping_thread = threading.Thread(
                target=self._perform_scraping,
                args=(website.id, start_url, max_depth, max_pages, use_selenium)
            )
            scraping_thread.start()
            
            return JsonResponse({
                'success': True,
                'scraping_job': {
                    'id': str(website.id),
                    'start_url': website.start_url,
                    'max_depth': website.max_depth,
                    'max_pages': website.max_pages,
                    'status': website.status
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _perform_scraping(self, website_id, start_url, max_depth, max_pages, use_selenium):
        """Perform the actual scraping in background"""
        try:
            website = ScrapedWebsite.objects.get(id=website_id)
            website.status = 'processing'
            website.save()
            
            extractor = WebContentExtractor(
                max_depth=max_depth,
                max_pages=max_pages,
                use_selenium=use_selenium
            )
            
            try:
                # Discover all links
                links = extractor.discover_links(start_url)
                
                total_words = 0
                pages_scraped = 0
                
                for i, url in enumerate(links):
                    result = extractor.scrape_page_content(url)
                    
                    if result['success']:
                        ScrapedPage.objects.create(
                            website=website,
                            url=url,
                            title=result.get('title', ''),
                            content=result.get('content', ''),
                            word_count=result.get('word_count', 0),
                            depth_level=0,  # Simplified depth tracking
                            scrape_duration_ms=result.get('processing_time_ms', 0),
                            content_type=result.get('content_type', 'text/html'),
                            status_code=result.get('status_code')
                        )
                        
                        total_words += result.get('word_count', 0)
                        pages_scraped += 1
                
                # Update website status
                website.pages_scraped = pages_scraped
                website.total_words = total_words
                website.status = 'completed'
                website.completed_at = timezone.now()
                website.save()
                
            finally:
                extractor.cleanup()
                
        except Exception as e:
            website = ScrapedWebsite.objects.get(id=website_id)
            website.status = 'failed'
            website.error_message = str(e)
            website.save()

class ScrapingJobStatusView(View):
    def get(self, request, job_id):
        try:
            website = ScrapedWebsite.objects.get(id=job_id)
            
            pages = []
            for page in website.pages.all()[:10]:  # Show first 10 pages
                pages.append({
                    'url': page.url,
                    'title': page.title,
                    'word_count': page.word_count,
                    'content_preview': page.content[:200] + '...' if len(page.content) > 200 else page.content
                })
            
            return JsonResponse({
                'id': str(website.id),
                'start_url': website.start_url,
                'domain': website.domain,
                'status': website.status,
                'pages_scraped': website.pages_scraped,
                'total_words': website.total_words,
                'error_message': website.error_message,
                'created_at': website.created_at.isoformat(),
                'completed_at': website.completed_at.isoformat() if website.completed_at else None,
                'pages': pages
            })
            
        except ScrapedWebsite.DoesNotExist:
            return JsonResponse({'error': 'Scraping job not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ScrapingJobListView(View):
    def get(self, request):
        try:
            websites = ScrapedWebsite.objects.all().order_by('-created_at')[:20]
            
            jobs = []
            for website in websites:
                jobs.append({
                    'id': str(website.id),
                    'start_url': website.start_url,
                    'domain': website.domain,
                    'status': website.status,
                    'pages_scraped': website.pages_scraped,
                    'total_words': website.total_words,
                    'created_at': website.created_at.isoformat()
                })
            
            return JsonResponse({'scraping_jobs': jobs})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 4. urls.py
from django.urls import path
from .views import WebScrapingView, ScrapingJobStatusView, ScrapingJobListView

urlpatterns = [
    path('web/scrape/', WebScrapingView.as_view()),
    path('web/scrape/<uuid:job_id>/status/', ScrapingJobStatusView.as_view()),
    path('web/scrape/jobs/', ScrapingJobListView.as_view()),
]