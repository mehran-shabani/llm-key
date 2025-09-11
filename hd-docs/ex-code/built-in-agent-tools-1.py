# Feature: Built-in Agent Tools
# Description: Comprehensive set of built-in tools for agents (web browsing, file ops, summarization)
# Library: Django, requests, beautifulsoup4, openai

# 1. models.py - Agent tools and execution tracking
from django.db import models
import uuid
import json

class AgentTool(models.Model):
    TOOL_CATEGORIES = [
        ('web', 'Web Operations'),
        ('file', 'File Operations'),
        ('data', 'Data Processing'),
        ('communication', 'Communication'),
        ('memory', 'Memory Management'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=TOOL_CATEGORIES)
    description = models.TextField()
    parameters_schema = models.JSONField()  # JSON schema for parameters
    handler_class = models.CharField(max_length=200)  # Python class name
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ToolExecution(models.Model):
    EXECUTION_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tool = models.ForeignKey(AgentTool, on_delete=models.CASCADE, related_name='executions')
    agent_name = models.CharField(max_length=100)
    session_id = models.UUIDField(null=True, blank=True)
    parameters = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS, default='pending')
    execution_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

# 2. agent_tools.py - Built-in tool implementations
import requests
import time
import tempfile
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgentTool(ABC):
    def __init__(self, tool_config):
        self.tool_config = tool_config
        self.name = tool_config.name
        self.description = tool_config.description
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against schema"""
        # Simplified validation (in real implementation, use jsonschema)
        required_params = self.tool_config.parameters_schema.get('required', [])
        
        for param in required_params:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")
        
        return True

class WebBrowsingTool(BaseAgentTool):
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            self.validate_parameters(parameters)
            query = parameters.get('query', '')
            
            if not query:
                return {'error': 'Search query is required'}
            
            # Simulate web search (in real implementation, use search APIs)
            search_results = await self._perform_search(query)
            
            return {
                'success': True,
                'query': query,
                'results': search_results,
                'total_results': len(search_results)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _perform_search(self, query: str) -> list:
        """Simulate web search results"""
        # In real implementation, use Google Search API, Bing API, etc.
        return [
            {
                'title': f'Search result 1 for: {query}',
                'url': 'https://example.com/result1',
                'snippet': f'This is a relevant snippet about {query}...',
                'score': 0.95
            },
            {
                'title': f'Search result 2 for: {query}',
                'url': 'https://example.com/result2',
                'snippet': f'Additional information about {query}...',
                'score': 0.87
            }
        ]

class WebScrapingTool(BaseAgentTool):
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape content from a webpage"""
        try:
            self.validate_parameters(parameters)
            url = parameters.get('url', '')
            
            if not url:
                return {'error': 'URL is required'}
            
            # Scrape webpage content
            content_data = await self._scrape_url(url)
            
            return {
                'success': True,
                'url': url,
                'title': content_data['title'],
                'content': content_data['content'],
                'word_count': len(content_data['content'].split()),
                'scraped_at': time.time()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _scrape_url(self, url: str) -> Dict[str, str]:
        """Scrape content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else 'No title'
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract main content
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
            clean_content = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'title': title.strip(),
                'content': clean_content
            }
            
        except Exception as e:
            raise Exception(f"Failed to scrape URL: {str(e)}")

class FileOperationsTool(BaseAgentTool):
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform file operations"""
        try:
            self.validate_parameters(parameters)
            action = parameters.get('action', '')
            filename = parameters.get('filename', '')
            content = parameters.get('content', '')
            
            if action == 'create':
                return await self._create_file(filename, content)
            elif action == 'read':
                return await self._read_file(filename)
            elif action == 'list':
                return await self._list_files(parameters.get('directory', '.'))
            elif action == 'delete':
                return await self._delete_file(filename)
            else:
                return {'error': f'Unsupported file operation: {action}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _create_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Create a file with content"""
        try:
            # In real implementation, save to secure agent workspace
            # For this example, we'll simulate file creation
            return {
                'success': True,
                'action': 'create',
                'filename': filename,
                'size_bytes': len(content.encode('utf-8')),
                'message': f'File {filename} created successfully'
            }
        except Exception as e:
            return {'error': f'Failed to create file: {str(e)}'}
    
    async def _read_file(self, filename: str) -> Dict[str, Any]:
        """Read file content"""
        # Simulate file reading
        return {
            'success': True,
            'action': 'read',
            'filename': filename,
            'content': f'Simulated content of {filename}',
            'size_bytes': 1024
        }
    
    async def _list_files(self, directory: str) -> Dict[str, Any]:
        """List files in directory"""
        # Simulate directory listing
        return {
            'success': True,
            'action': 'list',
            'directory': directory,
            'files': [
                {'name': 'document1.txt', 'size': 1024, 'type': 'file'},
                {'name': 'data.json', 'size': 2048, 'type': 'file'},
                {'name': 'subfolder', 'size': 0, 'type': 'directory'}
            ]
        }
    
    async def _delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a file"""
        # Simulate file deletion
        return {
            'success': True,
            'action': 'delete',
            'filename': filename,
            'message': f'File {filename} deleted successfully'
        }

class SummarizationTool(BaseAgentTool):
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize content or documents"""
        try:
            self.validate_parameters(parameters)
            
            content = parameters.get('content', '')
            document_id = parameters.get('document_id', '')
            summary_type = parameters.get('summary_type', 'brief')
            
            if document_id:
                # Summarize a specific document
                return await self._summarize_document(document_id, summary_type)
            elif content:
                # Summarize provided content
                return await self._summarize_content(content, summary_type)
            else:
                return {'error': 'Either content or document_id is required'}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _summarize_content(self, content: str, summary_type: str) -> Dict[str, Any]:
        """Summarize given content"""
        try:
            # Simulate content summarization (in real implementation, use LLM)
            word_count = len(content.split())
            
            if summary_type == 'brief':
                summary = f"Brief summary: This content contains {word_count} words discussing various topics."
            elif summary_type == 'detailed':
                summary = f"Detailed summary: This is a comprehensive analysis of {word_count} words covering multiple aspects of the subject matter."
            else:
                summary = f"Standard summary: Content analysis of {word_count} words."
            
            return {
                'success': True,
                'original_word_count': word_count,
                'summary_type': summary_type,
                'summary': summary,
                'compression_ratio': len(summary.split()) / word_count if word_count > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'Summarization failed: {str(e)}'}
    
    async def _summarize_document(self, document_id: str, summary_type: str) -> Dict[str, Any]:
        """Summarize a document by ID"""
        # In real implementation, fetch document from database
        return {
            'success': True,
            'document_id': document_id,
            'summary_type': summary_type,
            'summary': f'Simulated summary of document {document_id}',
            'original_word_count': 1500,
            'compression_ratio': 0.1
        }

class MemoryTool(BaseAgentTool):
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Manage agent memory and context"""
        try:
            self.validate_parameters(parameters)
            
            action = parameters.get('action', '')
            key = parameters.get('key', '')
            value = parameters.get('value', '')
            
            if action == 'store':
                return await self._store_memory(key, value)
            elif action == 'retrieve':
                return await self._retrieve_memory(key)
            elif action == 'list':
                return await self._list_memory()
            elif action == 'clear':
                return await self._clear_memory(key)
            else:
                return {'error': f'Unsupported memory action: {action}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    async def _store_memory(self, key: str, value: str) -> Dict[str, Any]:
        """Store information in agent memory"""
        # In real implementation, use persistent storage
        return {
            'success': True,
            'action': 'store',
            'key': key,
            'value_length': len(value),
            'message': f'Stored information under key: {key}'
        }
    
    async def _retrieve_memory(self, key: str) -> Dict[str, Any]:
        """Retrieve information from agent memory"""
        # Simulate memory retrieval
        return {
            'success': True,
            'action': 'retrieve',
            'key': key,
            'value': f'Simulated memory value for key: {key}',
            'found': True
        }
    
    async def _list_memory(self) -> Dict[str, Any]:
        """List all stored memory keys"""
        return {
            'success': True,
            'action': 'list',
            'keys': ['user_preferences', 'conversation_context', 'important_facts'],
            'total_keys': 3
        }
    
    async def _clear_memory(self, key: str = None) -> Dict[str, Any]:
        """Clear memory (specific key or all)"""
        if key:
            return {
                'success': True,
                'action': 'clear',
                'key': key,
                'message': f'Cleared memory for key: {key}'
            }
        else:
            return {
                'success': True,
                'action': 'clear_all',
                'message': 'Cleared all memory'
            }

# 3. tool_factory.py - Tool factory and registry
class AgentToolFactory:
    _tools_registry = {
        'web-browsing': WebBrowsingTool,
        'web-scraping': WebScrapingTool,
        'file-operations': FileOperationsTool,
        'summarization': SummarizationTool,
        'memory': MemoryTool,
    }
    
    @classmethod
    def register_tool(cls, name: str, tool_class):
        """Register a new tool class"""
        cls._tools_registry[name] = tool_class
    
    @classmethod
    def create_tool(cls, tool_name: str, tool_config) -> BaseAgentTool:
        """Create tool instance"""
        if tool_name not in cls._tools_registry:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_class = cls._tools_registry[tool_name]
        return tool_class(tool_config)
    
    @classmethod
    def get_available_tools(cls) -> list:
        """Get list of available tools"""
        return list(cls._tools_registry.keys())

# 4. tool_executor.py - Tool execution service
class ToolExecutor:
    @staticmethod
    async def execute_tool(tool_name: str, parameters: Dict[str, Any], 
                          agent_name: str = None, session_id: str = None) -> Dict[str, Any]:
        """Execute a tool and track the execution"""
        
        start_time = time.time()
        
        try:
            # Get tool configuration
            tool_config = AgentTool.objects.get(name=tool_name, is_active=True)
            
            # Create execution record
            execution = ToolExecution.objects.create(
                tool=tool_config,
                agent_name=agent_name or 'unknown',
                session_id=session_id,
                parameters=parameters,
                status='running'
            )
            
            try:
                # Create tool instance and execute
                tool_instance = AgentToolFactory.create_tool(tool_name, tool_config)
                result = await tool_instance.execute(parameters)
                
                # Update execution record
                execution_time = int((time.time() - start_time) * 1000)
                execution.result = result
                execution.status = 'completed' if result.get('success') else 'failed'
                execution.execution_time_ms = execution_time
                execution.completed_at = timezone.now()
                
                if not result.get('success'):
                    execution.error_message = result.get('error', 'Unknown error')
                
                execution.save()
                
                # Update tool usage count
                tool_config.usage_count += 1
                tool_config.save()
                
                return {
                    'execution_id': str(execution.id),
                    'tool_name': tool_name,
                    'execution_time_ms': execution_time,
                    **result
                }
                
            except Exception as e:
                # Update execution record with error
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.execution_time_ms = int((time.time() - start_time) * 1000)
                execution.completed_at = timezone.now()
                execution.save()
                
                raise e
                
        except AgentTool.DoesNotExist:
            return {'error': f'Tool {tool_name} not found'}
        except Exception as e:
            return {'error': str(e)}

# 5. views.py - Agent tools API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class ExecuteToolView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            tool_name = data.get('tool_name')
            parameters = data.get('parameters', {})
            agent_name = data.get('agent_name')
            session_id = data.get('session_id')
            
            if not tool_name:
                return JsonResponse({'error': 'Tool name is required'}, status=400)
            
            # Execute tool asynchronously
            async def execute():
                return await ToolExecutor.execute_tool(
                    tool_name, parameters, agent_name, session_id
                )
            
            result = asyncio.run(execute())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class AvailableToolsView(View):
    def get(self, request):
        try:
            tools = []
            
            for tool in AgentTool.objects.filter(is_active=True):
                tools.append({
                    'name': tool.name,
                    'display_name': tool.display_name,
                    'category': tool.category,
                    'description': tool.description,
                    'parameters_schema': tool.parameters_schema,
                    'usage_count': tool.usage_count
                })
            
            return JsonResponse({
                'tools': tools,
                'total_tools': len(tools),
                'available_categories': list(set(tool['category'] for tool in tools))
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ToolExecutionHistoryView(View):
    def get(self, request):
        try:
            executions = []
            
            for execution in ToolExecution.objects.all().order_by('-created_at')[:50]:
                executions.append({
                    'id': str(execution.id),
                    'tool_name': execution.tool.name,
                    'agent_name': execution.agent_name,
                    'status': execution.status,
                    'execution_time_ms': execution.execution_time_ms,
                    'created_at': execution.created_at.isoformat(),
                    'parameters': execution.parameters,
                    'result_preview': str(execution.result)[:200] + '...' if execution.result else None,
                    'error_message': execution.error_message
                })
            
            return JsonResponse({
                'executions': executions,
                'total_executions': len(executions)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 6. urls.py
from django.urls import path
from .views import ExecuteToolView, AvailableToolsView, ToolExecutionHistoryView

urlpatterns = [
    path('tools/execute/', ExecuteToolView.as_view()),
    path('tools/available/', AvailableToolsView.as_view()),
    path('tools/executions/', ToolExecutionHistoryView.as_view()),
]