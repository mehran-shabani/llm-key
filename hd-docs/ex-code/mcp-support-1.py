# Feature: Model Context Protocol (MCP) Support
# Description: MCP compatibility layer for integrating MCP servers as agent tools
# Library: Django, asyncio, websockets, subprocess

# 1. models.py - MCP server and tool management
from django.db import models
import uuid
import json

class MCPServer(models.Model):
    TRANSPORT_TYPES = [
        ('stdio', 'Standard Input/Output'),
        ('sse', 'Server-Sent Events'),
        ('http', 'HTTP Streamable'),
        ('websocket', 'WebSocket'),
    ]
    
    STATUS_CHOICES = [
        ('stopped', 'Stopped'),
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('failed', 'Failed'),
        ('crashed', 'Crashed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPES)
    command = models.TextField()  # Command to start the MCP server
    working_directory = models.CharField(max_length=500, blank=True)
    environment_variables = models.JSONField(default=dict)
    auto_start = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped')
    process_id = models.IntegerField(null=True, blank=True)
    port = models.IntegerField(null=True, blank=True)  # For HTTP/WebSocket transports
    endpoint = models.URLField(blank=True)  # For HTTP/SSE transports
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    restart_count = models.IntegerField(default=0)
    max_restarts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MCPTool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    server = models.ForeignKey(MCPServer, on_delete=models.CASCADE, related_name='tools')
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    description = models.TextField()
    parameters_schema = models.JSONField()  # JSON schema for tool parameters
    is_available = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('server', 'name')

class MCPToolExecution(models.Model):
    EXECUTION_STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tool = models.ForeignKey(MCPTool, on_delete=models.CASCADE, related_name='executions')
    agent_name = models.CharField(max_length=100, blank=True)
    session_id = models.UUIDField(null=True, blank=True)
    parameters = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EXECUTION_STATUS, default='pending')
    execution_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

# 2. mcp_client.py - MCP client implementation
import subprocess
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from django.utils import timezone

class MCPClient:
    def __init__(self, server_config):
        self.server_config = server_config
        self.server_name = server_config.name
        self.transport_type = server_config.transport_type
        self.command = server_config.command
        self.working_directory = server_config.working_directory
        self.environment = server_config.environment_variables
        
        self.process = None
        self.is_connected = False
        self.available_tools = []
    
    async def start_server(self) -> Dict[str, Any]:
        """Start the MCP server process"""
        try:
            if self.transport_type == 'stdio':
                return await self._start_stdio_server()
            elif self.transport_type == 'http':
                return await self._start_http_server()
            elif self.transport_type == 'sse':
                return await self._start_sse_server()
            else:
                return {'success': False, 'error': f'Unsupported transport type: {self.transport_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _start_stdio_server(self) -> Dict[str, Any]:
        """Start MCP server with stdio transport"""
        try:
            # Parse command
            cmd_parts = self.command.split()
            
            # Start process
            self.process = subprocess.Popen(
                cmd_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_directory or None,
                env={**os.environ, **self.environment},
                text=True,
                bufsize=0
            )
            
            # Wait a moment for process to start
            await asyncio.sleep(1)
            
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read()
                return {
                    'success': False,
                    'error': f'Process exited immediately: {stderr_output}'
                }
            
            # Initialize MCP connection
            init_result = await self._initialize_mcp_connection()
            
            if init_result['success']:
                self.is_connected = True
                
                # Update server status
                self.server_config.status = 'running'
                self.server_config.process_id = self.process.pid
                self.server_config.save()
                
                # Discover available tools
                await self._discover_tools()
            
            return init_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _start_http_server(self) -> Dict[str, Any]:
        """Start MCP server with HTTP transport"""
        # Simplified HTTP server startup
        return {
            'success': True,
            'message': 'HTTP MCP server started (simplified implementation)',
            'endpoint': self.server_config.endpoint
        }
    
    async def _start_sse_server(self) -> Dict[str, Any]:
        """Start MCP server with SSE transport"""
        # Simplified SSE server startup
        return {
            'success': True,
            'message': 'SSE MCP server started (simplified implementation)',
            'endpoint': self.server_config.endpoint
        }
    
    async def _initialize_mcp_connection(self) -> Dict[str, Any]:
        """Initialize MCP protocol connection"""
        try:
            # Send MCP initialization message
            init_message = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {
                        'tools': {},
                        'logging': {}
                    },
                    'clientInfo': {
                        'name': 'AnythingLLM',
                        'version': '1.0.0'
                    }
                }
            }
            
            # Send message to process
            if self.process and self.process.stdin:
                self.process.stdin.write(json.dumps(init_message) + '\n')
                self.process.stdin.flush()
                
                # Wait for response (simplified)
                await asyncio.sleep(0.5)
                
                return {'success': True, 'message': 'MCP connection initialized'}
            
            return {'success': False, 'error': 'No process stdin available'}
            
        except Exception as e:
            return {'success': False, 'error': f'MCP initialization failed: {str(e)}'}
    
    async def _discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from MCP server"""
        try:
            # Send tools/list request
            tools_request = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/list',
                'params': {}
            }
            
            if self.process and self.process.stdin:
                self.process.stdin.write(json.dumps(tools_request) + '\n')
                self.process.stdin.flush()
                
                # Simulate tool discovery response
                # In real implementation, parse actual MCP response
                discovered_tools = [
                    {
                        'name': f'{self.server_name}-example-tool',
                        'description': f'Example tool from {self.server_name} MCP server',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'input': {'type': 'string', 'description': 'Input parameter'}
                            },
                            'required': ['input']
                        }
                    }
                ]
                
                # Save discovered tools
                for tool_data in discovered_tools:
                    MCPTool.objects.update_or_create(
                        server=self.server_config,
                        name=tool_data['name'],
                        defaults={
                            'display_name': tool_data['name'].replace('-', ' ').title(),
                            'description': tool_data['description'],
                            'parameters_schema': tool_data['inputSchema'],
                            'is_available': True
                        }
                    )
                
                self.available_tools = discovered_tools
                return discovered_tools
            
            return []
            
        except Exception as e:
            print(f"Tool discovery failed: {str(e)}")
            return []
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via MCP protocol"""
        try:
            if not self.is_connected:
                return {'error': 'MCP server not connected'}
            
            # Send tool execution request
            tool_request = {
                'jsonrpc': '2.0',
                'id': int(time.time()),
                'method': 'tools/call',
                'params': {
                    'name': tool_name,
                    'arguments': parameters
                }
            }
            
            if self.process and self.process.stdin:
                self.process.stdin.write(json.dumps(tool_request) + '\n')
                self.process.stdin.flush()
                
                # Simulate tool execution result
                # In real implementation, parse actual MCP response
                return {
                    'success': True,
                    'result': f'Simulated result from {tool_name} with parameters: {parameters}',
                    'tool_name': tool_name,
                    'execution_time': 150
                }
            
            return {'error': 'No process stdin available'}
            
        except Exception as e:
            return {'error': f'Tool execution failed: {str(e)}'}
    
    async def stop_server(self) -> Dict[str, Any]:
        """Stop the MCP server"""
        try:
            if self.process:
                self.process.terminate()
                
                # Wait for process to terminate
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process_termination()),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # Force kill if it doesn't terminate gracefully
                    self.process.kill()
                
                self.process = None
                self.is_connected = False
                
                # Update server status
                self.server_config.status = 'stopped'
                self.server_config.process_id = None
                self.server_config.save()
                
                return {'success': True, 'message': 'MCP server stopped'}
            
            return {'success': True, 'message': 'MCP server was not running'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _wait_for_process_termination(self):
        """Wait for process to terminate"""
        while self.process and self.process.poll() is None:
            await asyncio.sleep(0.1)

# 3. mcp_manager.py - MCP server management service
import os

class MCPManager:
    _instances = {}  # Store MCP client instances
    
    @classmethod
    def get_client(cls, server_name: str) -> Optional[MCPClient]:
        """Get MCP client instance"""
        return cls._instances.get(server_name)
    
    @classmethod
    async def start_server(cls, server_name: str) -> Dict[str, Any]:
        """Start an MCP server"""
        try:
            server_config = MCPServer.objects.get(name=server_name)
            
            if server_name in cls._instances:
                return {'success': False, 'error': 'Server already running'}
            
            # Create client instance
            client = MCPClient(server_config)
            
            # Start the server
            result = await client.start_server()
            
            if result['success']:
                cls._instances[server_name] = client
                
                return {
                    'success': True,
                    'server_name': server_name,
                    'transport_type': server_config.transport_type,
                    'tools_discovered': len(client.available_tools),
                    'message': 'MCP server started successfully'
                }
            else:
                server_config.status = 'failed'
                server_config.error_message = result['error']
                server_config.save()
                
                return result
                
        except MCPServer.DoesNotExist:
            return {'success': False, 'error': f'MCP server {server_name} not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    async def stop_server(cls, server_name: str) -> Dict[str, Any]:
        """Stop an MCP server"""
        try:
            client = cls._instances.get(server_name)
            
            if not client:
                return {'success': False, 'error': 'Server not running'}
            
            result = await client.stop_server()
            
            if result['success']:
                del cls._instances[server_name]
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    async def execute_tool(cls, server_name: str, tool_name: str, 
                          parameters: Dict[str, Any], agent_name: str = None,
                          session_id: str = None) -> Dict[str, Any]:
        """Execute an MCP tool"""
        start_time = time.time()
        
        try:
            # Get MCP client
            client = cls._instances.get(server_name)
            
            if not client:
                return {'success': False, 'error': f'MCP server {server_name} not running'}
            
            # Get tool configuration
            try:
                tool_config = MCPTool.objects.get(
                    server__name=server_name,
                    name=tool_name,
                    is_available=True
                )
            except MCPTool.DoesNotExist:
                return {'success': False, 'error': f'Tool {tool_name} not found'}
            
            # Create execution record
            execution = MCPToolExecution.objects.create(
                tool=tool_config,
                agent_name=agent_name or 'unknown',
                session_id=session_id,
                parameters=parameters,
                status='running'
            )
            
            try:
                # Execute the tool
                result = await client.execute_tool(tool_name, parameters)
                
                execution_time = int((time.time() - start_time) * 1000)
                
                # Update execution record
                execution.result = result
                execution.status = 'completed' if result.get('success') else 'failed'
                execution.execution_time_ms = execution_time
                execution.completed_at = timezone.now()
                
                if not result.get('success'):
                    execution.error_message = result.get('error', 'Unknown error')
                
                execution.save()
                
                # Update tool usage
                tool_config.usage_count += 1
                tool_config.last_used = timezone.now()
                tool_config.save()
                
                return {
                    'execution_id': str(execution.id),
                    'execution_time_ms': execution_time,
                    **result
                }
                
            except Exception as e:
                execution_time = int((time.time() - start_time) * 1000)
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.execution_time_ms = execution_time
                execution.completed_at = timezone.now()
                execution.save()
                
                raise e
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    async def boot_auto_start_servers(cls) -> Dict[str, Any]:
        """Boot all servers marked for auto-start"""
        auto_start_servers = MCPServer.objects.filter(auto_start=True, status='stopped')
        
        results = {}
        
        for server in auto_start_servers:
            print(f"Auto-starting MCP server: {server.name}")
            result = await cls.start_server(server.name)
            results[server.name] = result
        
        return {
            'servers_started': len([r for r in results.values() if r['success']]),
            'servers_failed': len([r for r in results.values() if not r['success']]),
            'results': results
        }
    
    @classmethod
    def get_active_servers(cls) -> List[str]:
        """Get list of currently active MCP servers"""
        return list(cls._instances.keys())
    
    @classmethod
    async def health_check_servers(cls) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all running servers"""
        health_results = {}
        
        for server_name, client in cls._instances.items():
            try:
                # Simple health check - verify process is still running
                if client.process and client.process.poll() is None:
                    health_results[server_name] = {
                        'status': 'healthy',
                        'process_id': client.process.pid,
                        'uptime_seconds': time.time() - client.process.create_time() if hasattr(client.process, 'create_time') else None
                    }
                else:
                    health_results[server_name] = {
                        'status': 'unhealthy',
                        'error': 'Process not running'
                    }
                    
                    # Mark server as crashed
                    client.server_config.status = 'crashed'
                    client.server_config.save()
                    
            except Exception as e:
                health_results[server_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return health_results

# 4. views.py - MCP management API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class MCPServerControlView(View):
    def post(self, request, server_name, action):
        try:
            if action == 'start':
                async def start():
                    return await MCPManager.start_server(server_name)
                
                result = asyncio.run(start())
                
            elif action == 'stop':
                async def stop():
                    return await MCPManager.stop_server(server_name)
                
                result = asyncio.run(stop())
                
            elif action == 'restart':
                async def restart():
                    stop_result = await MCPManager.stop_server(server_name)
                    if stop_result['success']:
                        await asyncio.sleep(1)  # Wait a moment
                        return await MCPManager.start_server(server_name)
                    return stop_result
                
                result = asyncio.run(restart())
                
            else:
                return JsonResponse({'error': f'Invalid action: {action}'}, status=400)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MCPToolExecuteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            server_name = data.get('server_name')
            tool_name = data.get('tool_name')
            parameters = data.get('parameters', {})
            agent_name = data.get('agent_name')
            session_id = data.get('session_id')
            
            if not server_name or not tool_name:
                return JsonResponse({'error': 'server_name and tool_name are required'}, status=400)
            
            async def execute():
                return await MCPManager.execute_tool(
                    server_name, tool_name, parameters, agent_name, session_id
                )
            
            result = asyncio.run(execute())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class MCPServersView(View):
    def get(self, request):
        try:
            servers = []
            
            for server in MCPServer.objects.all():
                # Get tools for this server
                tools = []
                for tool in server.tools.filter(is_available=True):
                    tools.append({
                        'name': tool.name,
                        'display_name': tool.display_name,
                        'description': tool.description,
                        'usage_count': tool.usage_count,
                        'last_used': tool.last_used.isoformat() if tool.last_used else None
                    })
                
                servers.append({
                    'id': str(server.id),
                    'name': server.name,
                    'display_name': server.display_name,
                    'description': server.description,
                    'transport_type': server.transport_type,
                    'status': server.status,
                    'auto_start': server.auto_start,
                    'process_id': server.process_id,
                    'tools_count': len(tools),
                    'tools': tools,
                    'last_heartbeat': server.last_heartbeat.isoformat() if server.last_heartbeat else None,
                    'error_message': server.error_message,
                    'created_at': server.created_at.isoformat()
                })
            
            # Get active servers
            active_servers = MCPManager.get_active_servers()
            
            return JsonResponse({
                'servers': servers,
                'total_servers': len(servers),
                'active_servers': active_servers,
                'active_count': len(active_servers)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class MCPHealthCheckView(View):
    def get(self, request):
        try:
            async def health_check():
                return await MCPManager.health_check_servers()
            
            health_results = asyncio.run(health_check())
            
            return JsonResponse({
                'health_check': health_results,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class MCPToolsView(View):
    def get(self, request):
        try:
            tools = []
            
            for tool in MCPTool.objects.filter(is_available=True):
                tools.append({
                    'id': str(tool.id),
                    'name': tool.name,
                    'display_name': tool.display_name,
                    'description': tool.description,
                    'server_name': tool.server.name,
                    'server_status': tool.server.status,
                    'parameters_schema': tool.parameters_schema,
                    'usage_count': tool.usage_count,
                    'last_used': tool.last_used.isoformat() if tool.last_used else None
                })
            
            return JsonResponse({
                'tools': tools,
                'total_tools': len(tools),
                'servers_with_tools': len(set(tool['server_name'] for tool in tools))
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import (
    MCPServerControlView, MCPToolExecuteView, MCPServersView, 
    MCPHealthCheckView, MCPToolsView
)

urlpatterns = [
    path('mcp/servers/<str:server_name>/<str:action>/', MCPServerControlView.as_view()),
    path('mcp/tools/execute/', MCPToolExecuteView.as_view()),
    path('mcp/servers/', MCPServersView.as_view()),
    path('mcp/health/', MCPHealthCheckView.as_view()),
    path('mcp/tools/', MCPToolsView.as_view()),
]