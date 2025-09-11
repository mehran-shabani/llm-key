# Feature: Multi-Agent System (Aibitat)
# Description: Sophisticated multi-agent system with agent collaboration and tool usage
# Library: Django, Channels, asyncio, openai

# 1. models.py - Multi-agent system models
from django.db import models
import uuid
import json

class Agent(models.Model):
    AGENT_ROLES = [
        ('coordinator', 'Coordinator'),
        ('researcher', 'Researcher'),
        ('writer', 'Writer'),
        ('reviewer', 'Reviewer'),
        ('analyst', 'Analyst'),
        ('specialist', 'Specialist'),
        ('human', 'Human'),
    ]
    
    INTERRUPT_MODES = [
        ('never', 'Never'),
        ('always', 'Always'),
        ('on_error', 'On Error'),
        ('on_request', 'On Request'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=AGENT_ROLES)
    system_prompt = models.TextField()
    interrupt_mode = models.CharField(max_length=20, choices=INTERRUPT_MODES, default='never')
    max_iterations = models.IntegerField(default=10)
    available_functions = models.JSONField(default=list)  # List of function names
    llm_provider = models.CharField(max_length=50, default='openai')
    llm_model = models.CharField(max_length=100, default='gpt-4')
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AgentSession(models.Model):
    SESSION_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('interrupted', 'Interrupted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    participating_agents = models.ManyToManyField(Agent, related_name='sessions')
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='active')
    max_rounds = models.IntegerField(default=100)
    current_round = models.IntegerField(default=0)
    session_data = models.JSONField(default=dict)  # Store session state
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class AgentMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('agent', 'Agent Message'),
        ('system', 'System Message'),
        ('function_call', 'Function Call'),
        ('function_result', 'Function Result'),
        ('error', 'Error Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(AgentSession, on_delete=models.CASCADE, related_name='messages')
    from_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    to_agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict)  # Store additional message data
    round_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class AgentFunction(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField()
    parameters_schema = models.JSONField()  # JSON schema for function parameters
    handler_module = models.CharField(max_length=200)  # Python module path
    handler_function = models.CharField(max_length=100)  # Function name
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 2. agent_system.py - Multi-agent system core
import asyncio
import json
import importlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils import timezone

class MultiAgentSystem:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session = None
        self.agents = {}
        self.functions = {}
        self.message_history = []
        self.current_round = 0
        self.max_rounds = 100
        self.is_running = False
    
    async def initialize_session(self):
        """Initialize the agent session"""
        try:
            self.session = AgentSession.objects.get(id=self.session_id)
            self.max_rounds = self.session.max_rounds
            self.current_round = self.session.current_round
            
            # Load participating agents
            for agent in self.session.participating_agents.all():
                self.agents[agent.name] = agent
            
            # Load available functions
            for agent in self.agents.values():
                for func_name in agent.available_functions:
                    if func_name not in self.functions:
                        try:
                            func = AgentFunction.objects.get(name=func_name, is_active=True)
                            self.functions[func_name] = func
                        except AgentFunction.DoesNotExist:
                            print(f"Warning: Function {func_name} not found")
            
            # Load message history
            messages = AgentMessage.objects.filter(session=self.session).order_by('created_at')
            self.message_history = list(messages)
            
            return True
            
        except AgentSession.DoesNotExist:
            print(f"Session {self.session_id} not found")
            return False
    
    async def add_message(self, from_agent: str, to_agent: str, content: str, 
                         message_type: str = 'agent', metadata: dict = None):
        """Add a message to the conversation"""
        from_agent_obj = self.agents.get(from_agent)
        to_agent_obj = self.agents.get(to_agent)
        
        message = AgentMessage.objects.create(
            session=self.session,
            from_agent=from_agent_obj,
            to_agent=to_agent_obj,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            round_number=self.current_round
        )
        
        self.message_history.append(message)
        return message
    
    async def execute_function(self, function_name: str, parameters: dict) -> dict:
        """Execute an agent function"""
        if function_name not in self.functions:
            return {'error': f'Function {function_name} not available'}
        
        func_config = self.functions[function_name]
        
        try:
            # Import the handler module
            module = importlib.import_module(func_config.handler_module)
            handler = getattr(module, func_config.handler_function)
            
            # Execute the function
            result = await handler(**parameters)
            
            return {'success': True, 'result': result}
            
        except Exception as e:
            return {'error': f'Function execution failed: {str(e)}'}
    
    async def generate_agent_response(self, agent_name: str, conversation_context: list) -> dict:
        """Generate response from an agent using LLM"""
        agent = self.agents[agent_name]
        
        try:
            # Build messages for LLM
            messages = [
                {"role": "system", "content": agent.system_prompt}
            ]
            
            # Add conversation history
            for msg in conversation_context[-10:]:  # Last 10 messages for context
                role = "user" if msg.message_type == "user" else "assistant"
                messages.append({"role": role, "content": msg.content})
            
            # Simulate LLM call (in real implementation, use actual LLM)
            response_content = f"[Agent {agent.display_name}]: This is a simulated response based on the conversation context. In a real implementation, this would be generated by {agent.llm_provider} {agent.llm_model}."
            
            # Check if agent wants to call a function
            function_calls = []
            if agent.available_functions and "research" in conversation_context[-1].content.lower():
                function_calls.append({
                    "name": "web_search",
                    "parameters": {"query": "relevant search query"}
                })
            
            return {
                'success': True,
                'content': response_content,
                'function_calls': function_calls
            }
            
        except Exception as e:
            return {'error': f'Agent response generation failed: {str(e)}'}
    
    async def run_conversation_round(self, initial_message: str = None) -> dict:
        """Run one round of multi-agent conversation"""
        if self.current_round >= self.max_rounds:
            return {'status': 'max_rounds_reached'}
        
        self.current_round += 1
        round_results = []
        
        try:
            # If this is the first round, add initial message
            if initial_message and self.current_round == 1:
                await self.add_message(
                    from_agent='human',
                    to_agent='coordinator',
                    content=initial_message,
                    message_type='user'
                )
            
            # Get list of active agents for this round
            active_agents = [name for name, agent in self.agents.items() if agent.is_active]
            
            # Coordinate agent interactions
            for agent_name in active_agents:
                agent = self.agents[agent_name]
                
                # Skip human agents in automated rounds
                if agent.role == 'human' and agent.interrupt_mode != 'always':
                    continue
                
                # Generate agent response
                response = await self.generate_agent_response(
                    agent_name, 
                    self.message_history
                )
                
                if response.get('success'):
                    # Add agent message
                    await self.add_message(
                        from_agent=agent_name,
                        to_agent='all',  # Broadcast to all agents
                        content=response['content'],
                        message_type='agent'
                    )
                    
                    # Execute any function calls
                    for func_call in response.get('function_calls', []):
                        func_result = await self.execute_function(
                            func_call['name'],
                            func_call['parameters']
                        )
                        
                        # Add function result message
                        await self.add_message(
                            from_agent='system',
                            to_agent=agent_name,
                            content=json.dumps(func_result),
                            message_type='function_result',
                            metadata={'function_name': func_call['name']}
                        )
                    
                    round_results.append({
                        'agent': agent_name,
                        'success': True,
                        'message_count': 1 + len(response.get('function_calls', []))
                    })
                
                else:
                    # Handle agent error
                    await self.add_message(
                        from_agent='system',
                        to_agent=agent_name,
                        content=f"Error: {response['error']}",
                        message_type='error'
                    )
                    
                    round_results.append({
                        'agent': agent_name,
                        'success': False,
                        'error': response['error']
                    })
            
            # Update session
            self.session.current_round = self.current_round
            self.session.save()
            
            return {
                'status': 'completed',
                'round': self.current_round,
                'results': round_results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'round': self.current_round,
                'error': str(e)
            }
    
    async def run_full_conversation(self, initial_message: str, max_rounds: int = None) -> dict:
        """Run complete multi-agent conversation"""
        if max_rounds:
            self.max_rounds = max_rounds
        
        self.is_running = True
        conversation_results = []
        
        try:
            while self.current_round < self.max_rounds and self.is_running:
                round_result = await self.run_conversation_round(
                    initial_message if self.current_round == 0 else None
                )
                
                conversation_results.append(round_result)
                
                if round_result['status'] in ['max_rounds_reached', 'error']:
                    break
                
                # Check for natural conversation end
                last_messages = self.message_history[-3:]
                if any('complete' in msg.content.lower() or 'finished' in msg.content.lower() 
                      for msg in last_messages):
                    break
            
            # Mark session as completed
            self.session.status = 'completed'
            self.session.completed_at = timezone.now()
            self.session.save()
            
            return {
                'success': True,
                'total_rounds': self.current_round,
                'total_messages': len(self.message_history),
                'results': conversation_results
            }
            
        except Exception as e:
            # Mark session as failed
            self.session.status = 'failed'
            self.session.session_data['error'] = str(e)
            self.session.save()
            
            return {
                'success': False,
                'error': str(e),
                'total_rounds': self.current_round,
                'results': conversation_results
            }
        finally:
            self.is_running = False

# 3. agent_functions.py - Built-in agent functions
async def web_search_function(query: str, max_results: int = 5) -> dict:
    """Web search function for agents"""
    try:
        # Simulate web search (in real implementation, use actual search API)
        results = [
            {
                'title': f'Search result {i+1} for: {query}',
                'url': f'https://example.com/result-{i+1}',
                'snippet': f'This is a simulated search result snippet for query: {query}'
            }
            for i in range(min(max_results, 3))
        ]
        
        return {
            'query': query,
            'results': results,
            'total_found': len(results)
        }
        
    except Exception as e:
        return {'error': str(e)}

async def file_operation_function(operation: str, filename: str, content: str = None) -> dict:
    """File operation function for agents"""
    try:
        if operation == 'read':
            # Simulate file read
            return {
                'operation': 'read',
                'filename': filename,
                'content': f'Simulated content of {filename}',
                'success': True
            }
        
        elif operation == 'write':
            # Simulate file write
            return {
                'operation': 'write',
                'filename': filename,
                'bytes_written': len(content) if content else 0,
                'success': True
            }
        
        elif operation == 'list':
            # Simulate directory listing
            return {
                'operation': 'list',
                'directory': filename,
                'files': ['file1.txt', 'file2.py', 'file3.json'],
                'success': True
            }
        
        else:
            return {'error': f'Unsupported operation: {operation}'}
            
    except Exception as e:
        return {'error': str(e)}

async def memory_function(action: str, key: str = None, value: str = None) -> dict:
    """Memory function for agents to store/retrieve information"""
    # In real implementation, this would use a persistent storage
    memory_store = {}
    
    try:
        if action == 'store' and key and value:
            memory_store[key] = value
            return {'action': 'store', 'key': key, 'success': True}
        
        elif action == 'retrieve' and key:
            value = memory_store.get(key, 'Not found')
            return {'action': 'retrieve', 'key': key, 'value': value, 'success': True}
        
        elif action == 'list':
            return {'action': 'list', 'keys': list(memory_store.keys()), 'success': True}
        
        else:
            return {'error': 'Invalid action or missing parameters'}
            
    except Exception as e:
        return {'error': str(e)}

# 4. views.py - Multi-agent system API endpoints
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import asyncio

@method_decorator(csrf_exempt, name='dispatch')
class CreateAgentSessionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            session = AgentSession.objects.create(
                name=data.get('name', 'Multi-Agent Session'),
                description=data.get('description', ''),
                max_rounds=data.get('max_rounds', 100)
            )
            
            # Add participating agents
            agent_names = data.get('agents', [])
            for agent_name in agent_names:
                try:
                    agent = Agent.objects.get(name=agent_name, is_active=True)
                    session.participating_agents.add(agent)
                except Agent.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'session': {
                    'id': str(session.id),
                    'name': session.name,
                    'status': session.status,
                    'max_rounds': session.max_rounds,
                    'participating_agents': [agent.name for agent in session.participating_agents.all()]
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RunAgentConversationView(View):
    def post(self, request, session_id):
        try:
            data = json.loads(request.body)
            initial_message = data.get('message', '')
            max_rounds = data.get('max_rounds')
            
            # Create and run multi-agent system
            async def run_conversation():
                agent_system = MultiAgentSystem(session_id)
                
                if not await agent_system.initialize_session():
                    return {'error': 'Failed to initialize session'}
                
                return await agent_system.run_full_conversation(initial_message, max_rounds)
            
            # Run async function
            result = asyncio.run(run_conversation())
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class AgentSessionDetailView(View):
    def get(self, request, session_id):
        try:
            session = AgentSession.objects.get(id=session_id)
            
            # Get messages
            messages = []
            for msg in session.messages.all().order_by('created_at'):
                messages.append({
                    'id': str(msg.id),
                    'from_agent': msg.from_agent.name if msg.from_agent else None,
                    'to_agent': msg.to_agent.name if msg.to_agent else None,
                    'type': msg.message_type,
                    'content': msg.content,
                    'round': msg.round_number,
                    'created_at': msg.created_at.isoformat(),
                    'metadata': msg.metadata
                })
            
            return JsonResponse({
                'session': {
                    'id': str(session.id),
                    'name': session.name,
                    'description': session.description,
                    'status': session.status,
                    'current_round': session.current_round,
                    'max_rounds': session.max_rounds,
                    'participating_agents': [
                        {
                            'name': agent.name,
                            'display_name': agent.display_name,
                            'role': agent.role
                        }
                        for agent in session.participating_agents.all()
                    ],
                    'created_at': session.created_at.isoformat(),
                    'completed_at': session.completed_at.isoformat() if session.completed_at else None
                },
                'messages': messages,
                'total_messages': len(messages)
            })
            
        except AgentSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class AgentsListView(View):
    def get(self, request):
        try:
            agents = []
            
            for agent in Agent.objects.filter(is_active=True):
                agents.append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'display_name': agent.display_name,
                    'role': agent.role,
                    'interrupt_mode': agent.interrupt_mode,
                    'available_functions': agent.available_functions,
                    'llm_provider': agent.llm_provider,
                    'llm_model': agent.llm_model
                })
            
            return JsonResponse({'agents': agents})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import (
    CreateAgentSessionView, RunAgentConversationView, 
    AgentSessionDetailView, AgentsListView
)

urlpatterns = [
    path('agents/session/create/', CreateAgentSessionView.as_view()),
    path('agents/session/<uuid:session_id>/run/', RunAgentConversationView.as_view()),
    path('agents/session/<uuid:session_id>/', AgentSessionDetailView.as_view()),
    path('agents/', AgentsListView.as_view()),
]