import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta

from .models import WorkspaceChat
from workspaces.models import Workspace, WorkspaceAgentInvocation
from authentication.models import User
from system_settings.models import EventLog, Telemetry


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.workspace_slug = self.scope['url_route']['kwargs']['workspace_slug']
        self.room_group_name = f'chat_{self.workspace_slug}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to chat'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'feedback':
                await self.handle_feedback(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_chat_message(self, data):
        """Process chat message."""
        message = data.get('message')
        user = self.scope.get('user')
        
        if not message:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message is required'
            }))
            return
        
        # Check user chat limit
        can_send = await self.check_user_chat_limit(user)
        if not can_send:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'You have reached your daily chat limit'
            }))
            return
        
        # Get workspace
        workspace = await self.get_workspace()
        if not workspace:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Workspace not found'
            }))
            return
        
        # Generate chat ID
        chat_id = str(uuid.uuid4())
        
        # Send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'chat_start',
            'chat_id': chat_id,
            'message': 'Processing your message...'
        }))
        
        # TODO: Integrate with actual LLM provider
        # For now, simulate a response
        response = f"This is a simulated response to: {message}"
        
        # Stream response tokens
        for token in response.split():
            await self.send(text_data=json.dumps({
                'type': 'chat_token',
                'chat_id': chat_id,
                'token': token + ' '
            }))
            # Add small delay to simulate streaming
            import asyncio
            await asyncio.sleep(0.1)
        
        # Save chat to database
        chat = await self.save_chat(workspace, user, message, response)
        
        # Send completion
        await self.send(text_data=json.dumps({
            'type': 'chat_complete',
            'chat_id': chat_id,
            'db_id': chat.id,
            'response': response
        }))
        
        # Log telemetry
        await self.log_chat_telemetry(workspace, user)
    
    async def handle_typing_indicator(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        user = self.scope.get('user')
        
        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user': user.username if user else 'Anonymous',
                'is_typing': is_typing
            }
        )
    
    async def handle_feedback(self, data):
        """Handle chat feedback."""
        chat_id = data.get('chat_id')
        feedback = data.get('feedback')
        
        if not chat_id or feedback is None:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'chat_id and feedback are required'
            }))
            return
        
        # Update chat feedback
        await self.update_chat_feedback(chat_id, feedback)
        
        await self.send(text_data=json.dumps({
            'type': 'feedback_received',
            'chat_id': chat_id,
            'feedback': feedback
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    @database_sync_to_async
    def get_workspace(self):
        """Get workspace from slug."""
        try:
            return Workspace.objects.get(slug=self.workspace_slug)
        except Workspace.DoesNotExist:
            return None
    
    @database_sync_to_async
    def check_user_chat_limit(self, user):
        """Check if user can send chat."""
        if not user or not user.daily_message_limit:
            return True
        
        last_24_hours = timezone.now() - timedelta(hours=24)
        chat_count = WorkspaceChat.objects.filter(
            user=user,
            created_at__gte=last_24_hours
        ).count()
        
        return chat_count < user.daily_message_limit
    
    @database_sync_to_async
    def save_chat(self, workspace, user, prompt, response):
        """Save chat to database."""
        return WorkspaceChat.objects.create(
            workspace_id=workspace.id,
            prompt=prompt,
            response=response,
            user=user if user and user.is_authenticated else None
        )
    
    @database_sync_to_async
    def update_chat_feedback(self, chat_id, feedback):
        """Update chat feedback."""
        try:
            chat = WorkspaceChat.objects.get(id=chat_id)
            chat.feedback_score = feedback
            chat.save()
            return True
        except WorkspaceChat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def log_chat_telemetry(self, workspace, user):
        """Log chat telemetry."""
        EventLog.log_event(
            'websocket_chat_sent',
            {'workspace_name': workspace.name},
            user.id if user else None
        )
        
        Telemetry.send_telemetry(
            'websocket_chat_sent',
            {'workspace_id': workspace.id},
            user.id if user else None
        )


class AgentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for agent interactions."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.workspace_slug = self.scope['url_route']['kwargs']['workspace_slug']
        self.room_group_name = f'agent_{self.workspace_slug}'
        self.invocation_uuid = None
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to agent'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Close any open invocation
        if self.invocation_uuid:
            await self.close_invocation()
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'invoke':
                await self.handle_agent_invocation(data)
            elif message_type == 'tool_response':
                await self.handle_tool_response(data)
            elif message_type == 'close':
                await self.handle_close_invocation()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_agent_invocation(self, data):
        """Handle agent invocation."""
        prompt = data.get('prompt')
        user = self.scope.get('user')
        
        if not prompt:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Prompt is required'
            }))
            return
        
        # Get workspace
        workspace = await self.get_workspace()
        if not workspace:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Workspace not found'
            }))
            return
        
        # Create invocation
        invocation = await self.create_invocation(workspace, user, prompt)
        self.invocation_uuid = str(invocation.uuid)
        
        # Send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'invocation_started',
            'uuid': self.invocation_uuid,
            'message': 'Agent invocation started'
        }))
        
        # TODO: Implement actual agent logic
        # For now, simulate agent response
        await self.send(text_data=json.dumps({
            'type': 'agent_message',
            'uuid': self.invocation_uuid,
            'message': 'I am processing your request...'
        }))
        
        # Simulate tool call
        await self.send(text_data=json.dumps({
            'type': 'tool_call',
            'uuid': self.invocation_uuid,
            'tool': 'web_search',
            'parameters': {'query': 'example search'},
            'message': 'Searching the web...'
        }))
    
    async def handle_tool_response(self, data):
        """Handle tool response from client."""
        tool = data.get('tool')
        result = data.get('result')
        
        if not self.invocation_uuid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No active invocation'
            }))
            return
        
        # Process tool response
        await self.send(text_data=json.dumps({
            'type': 'tool_result',
            'uuid': self.invocation_uuid,
            'tool': tool,
            'message': f'Received result from {tool}'
        }))
        
        # Continue agent processing
        # TODO: Implement actual agent logic
    
    async def handle_close_invocation(self):
        """Handle closing agent invocation."""
        if self.invocation_uuid:
            await self.close_invocation()
            
            await self.send(text_data=json.dumps({
                'type': 'invocation_closed',
                'uuid': self.invocation_uuid,
                'message': 'Agent invocation closed'
            }))
            
            self.invocation_uuid = None
    
    @database_sync_to_async
    def get_workspace(self):
        """Get workspace from slug."""
        try:
            return Workspace.objects.get(slug=self.workspace_slug)
        except Workspace.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_invocation(self, workspace, user, prompt):
        """Create agent invocation."""
        return WorkspaceAgentInvocation.objects.create(
            workspace=workspace,
            user=user if user and user.is_authenticated else None,
            prompt=prompt
        )
    
    @database_sync_to_async
    def close_invocation(self):
        """Close agent invocation."""
        try:
            invocation = WorkspaceAgentInvocation.objects.get(uuid=self.invocation_uuid)
            invocation.closed = True
            invocation.save()
            return True
        except WorkspaceAgentInvocation.DoesNotExist:
            return False