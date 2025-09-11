# Feature: Commercial LLM Providers
# Description: Support for multiple commercial LLM providers (OpenAI, Anthropic, etc.)
# Library: Django, openai, anthropic, requests

# 1. models.py - LLM provider configuration
from django.db import models
import json

class LLMProvider(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('azure_openai', 'Azure OpenAI'),
        ('google_gemini', 'Google Gemini'),
        ('aws_bedrock', 'AWS Bedrock'),
        ('cohere', 'Cohere'),
        ('groq', 'Groq'),
        ('perplexity', 'Perplexity'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=500)  # Encrypted in production
    base_url = models.URLField(blank=True)  # For custom endpoints
    default_model = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    max_tokens = models.IntegerField(default=4000)
    temperature = models.FloatField(default=0.7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LLMModel(models.Model):
    provider = models.ForeignKey(LLMProvider, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    context_window = models.IntegerField()  # Token limit
    supports_streaming = models.BooleanField(default=True)
    supports_functions = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    cost_per_1k_input_tokens = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    cost_per_1k_output_tokens = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    
    class Meta:
        unique_together = ('provider', 'name')

# 2. llm_providers.py - Provider implementations
import openai
import anthropic
import requests
from abc import ABC, abstractmethod
from django.conf import settings

class BaseLLMProvider(ABC):
    def __init__(self, api_key, model_name, temperature=0.7, max_tokens=4000):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def generate_completion(self, messages, stream=False):
        """Generate completion from messages"""
        pass
    
    @abstractmethod
    def get_available_models(self):
        """Get list of available models"""
        pass
    
    def format_messages(self, system_prompt, user_message, chat_history=None):
        """Format messages for the provider"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add chat history
        if chat_history:
            for msg in chat_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_completion(self, messages, stream=False):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_stream_response(self, stream):
        """Handle streaming response from OpenAI"""
        def stream_generator():
            try:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield {
                            'type': 'content',
                            'content': chunk.choices[0].delta.content
                        }
                yield {'type': 'done'}
            except Exception as e:
                yield {'type': 'error', 'error': str(e)}
        
        return {'success': True, 'stream': stream_generator()}
    
    def get_available_models(self):
        try:
            models = self.client.models.list()
            return [
                {
                    'id': model.id,
                    'name': model.id,
                    'created': model.created,
                    'owned_by': model.owned_by
                }
                for model in models.data
                if 'gpt' in model.id.lower()
            ]
        except Exception as e:
            return []

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_completion(self, messages, stream=False):
        try:
            # Anthropic requires system message to be separate
            system_message = None
            formatted_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    formatted_messages.append(msg)
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_message,
                messages=formatted_messages,
                stream=stream
            )
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return {
                    'success': True,
                    'content': response.content[0].text,
                    'usage': {
                        'prompt_tokens': response.usage.input_tokens,
                        'completion_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                    }
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_stream_response(self, stream):
        """Handle streaming response from Anthropic"""
        def stream_generator():
            try:
                for event in stream:
                    if event.type == 'content_block_delta':
                        yield {
                            'type': 'content',
                            'content': event.delta.text
                        }
                    elif event.type == 'message_stop':
                        yield {'type': 'done'}
            except Exception as e:
                yield {'type': 'error', 'error': str(e)}
        
        return {'success': True, 'stream': stream_generator()}
    
    def get_available_models(self):
        # Anthropic doesn't have a models API, return known models
        return [
            {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet'},
            {'id': 'claude-3-5-haiku-20241022', 'name': 'Claude 3.5 Haiku'},
            {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus'},
        ]

class GenericOpenAIProvider(BaseLLMProvider):
    """Generic provider for OpenAI-compatible APIs (Groq, Perplexity, etc.)"""
    
    def __init__(self, base_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_completion(self, messages, stream=False):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'usage': getattr(response, 'usage', None)
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_stream_response(self, stream):
        """Handle streaming response"""
        def stream_generator():
            try:
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield {
                            'type': 'content',
                            'content': chunk.choices[0].delta.content
                        }
                yield {'type': 'done'}
            except Exception as e:
                yield {'type': 'error', 'error': str(e)}
        
        return {'success': True, 'stream': stream_generator()}
    
    def get_available_models(self):
        try:
            models = self.client.models.list()
            return [{'id': model.id, 'name': model.id} for model in models.data]
        except Exception as e:
            return []

# 3. llm_factory.py - Provider factory
class LLMProviderFactory:
    @staticmethod
    def create_provider(provider_name, api_key, model_name, base_url=None, **kwargs):
        """Create LLM provider instance"""
        
        if provider_name == 'openai':
            return OpenAIProvider(api_key, model_name, **kwargs)
        
        elif provider_name == 'anthropic':
            return AnthropicProvider(api_key, model_name, **kwargs)
        
        elif provider_name in ['groq', 'perplexity', 'azure_openai']:
            # These use OpenAI-compatible APIs
            provider_urls = {
                'groq': 'https://api.groq.com/openai/v1',
                'perplexity': 'https://api.perplexity.ai',
                'azure_openai': base_url  # Custom base URL for Azure
            }
            return GenericOpenAIProvider(
                provider_urls.get(provider_name, base_url),
                api_key, model_name, **kwargs
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

# 4. views.py - LLM provider API endpoints
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class LLMChatView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            provider_name = data.get('provider', 'openai')
            model_name = data.get('model')
            message = data.get('message', '')
            system_prompt = data.get('system_prompt', '')
            chat_history = data.get('chat_history', [])
            stream = data.get('stream', False)
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get provider configuration
            try:
                provider_config = LLMProvider.objects.get(name=provider_name, is_active=True)
            except LLMProvider.DoesNotExist:
                return JsonResponse({'error': f'Provider {provider_name} not configured'}, status=400)
            
            # Use specified model or default
            model = model_name or provider_config.default_model
            
            # Create provider instance
            provider = LLMProviderFactory.create_provider(
                provider_name=provider_config.name,
                api_key=provider_config.api_key,
                model_name=model,
                base_url=provider_config.base_url,
                temperature=provider_config.temperature,
                max_tokens=provider_config.max_tokens
            )
            
            # Format messages
            messages = provider.format_messages(system_prompt, message, chat_history)
            
            # Generate completion
            if stream:
                return self._handle_streaming_response(provider, messages)
            else:
                result = provider.generate_completion(messages, stream=False)
                
                if result['success']:
                    return JsonResponse({
                        'success': True,
                        'response': result['content'],
                        'usage': result.get('usage'),
                        'provider': provider_name,
                        'model': model
                    })
                else:
                    return JsonResponse({'error': result['error']}, status=500)
                    
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _handle_streaming_response(self, provider, messages):
        """Handle streaming response"""
        result = provider.generate_completion(messages, stream=True)
        
        if not result['success']:
            return JsonResponse({'error': result['error']}, status=500)
        
        def stream_response():
            for chunk in result['stream']:
                yield f"data: {json.dumps(chunk)}\n\n"
        
        response = StreamingHttpResponse(stream_response(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        return response

class LLMProvidersView(View):
    def get(self, request):
        """Get available LLM providers and their models"""
        try:
            providers = []
            
            for provider_config in LLMProvider.objects.filter(is_active=True):
                # Get available models for this provider
                try:
                    provider = LLMProviderFactory.create_provider(
                        provider_name=provider_config.name,
                        api_key=provider_config.api_key,
                        model_name=provider_config.default_model
                    )
                    available_models = provider.get_available_models()
                except Exception:
                    available_models = []
                
                providers.append({
                    'name': provider_config.name,
                    'display_name': provider_config.display_name,
                    'default_model': provider_config.default_model,
                    'available_models': available_models,
                    'supports_streaming': True,
                    'max_tokens': provider_config.max_tokens
                })
            
            return JsonResponse({'providers': providers})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class LLMProviderConfigView(View):
    def get(self, request, provider_name):
        """Get specific provider configuration"""
        try:
            provider = LLMProvider.objects.get(name=provider_name)
            
            return JsonResponse({
                'name': provider.name,
                'display_name': provider.display_name,
                'default_model': provider.default_model,
                'is_active': provider.is_active,
                'max_tokens': provider.max_tokens,
                'temperature': provider.temperature,
                'base_url': provider.base_url
            })
            
        except LLMProvider.DoesNotExist:
            return JsonResponse({'error': 'Provider not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import LLMChatView, LLMProvidersView, LLMProviderConfigView

urlpatterns = [
    path('llm/chat/', LLMChatView.as_view()),
    path('llm/providers/', LLMProvidersView.as_view()),
    path('llm/providers/<str:provider_name>/', LLMProviderConfigView.as_view()),
]