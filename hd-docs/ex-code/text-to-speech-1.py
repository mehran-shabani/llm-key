# Feature: Text-to-Speech (TTS) - Django Backend
# Description: Convert text to speech using multiple TTS providers
# Library: Django, openai, elevenlabs, gTTS, pydub

# 1. models.py - TTS configuration and history
from django.db import models
import uuid

class TTSProvider(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI TTS'),
        ('elevenlabs', 'ElevenLabs'),
        ('google', 'Google TTS'),
        ('azure', 'Azure Cognitive Services'),
        ('aws', 'Amazon Polly'),
        ('native', 'Browser Native'),
    ]
    
    name = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=500, blank=True)  # Encrypted in production
    base_url = models.URLField(blank=True)
    configuration = models.JSONField(default=dict)  # Provider-specific settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class TTSVoice(models.Model):
    provider = models.ForeignKey(TTSProvider, on_delete=models.CASCADE, related_name='voices')
    voice_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('neutral', 'Neutral')])
    description = models.TextField(blank=True)
    sample_url = models.URLField(blank=True)
    is_premium = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('provider', 'voice_id')

class TTSRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    provider = models.ForeignKey(TTSProvider, on_delete=models.CASCADE)
    voice = models.ForeignKey(TTSVoice, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    audio_file = models.FileField(upload_to='tts_audio/', blank=True)
    audio_format = models.CharField(max_length=10, default='mp3')
    duration_seconds = models.FloatField(null=True, blank=True)
    file_size_bytes = models.IntegerField(null=True, blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 2. tts_providers.py - TTS provider implementations
import requests
import tempfile
import time
from io import BytesIO
from abc import ABC, abstractmethod
from django.core.files.base import ContentFile

class BaseTTSProvider(ABC):
    def __init__(self, config):
        self.config = config
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
    
    @abstractmethod
    def synthesize_speech(self, text, voice_id=None, **kwargs):
        """Convert text to speech"""
        pass
    
    @abstractmethod
    def get_available_voices(self):
        """Get list of available voices"""
        pass
    
    def validate_text(self, text):
        """Validate input text"""
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        if len(text) > 4000:  # Most TTS services have character limits
            raise ValueError("Text too long (max 4000 characters)")
        
        return text.strip()

class OpenAITTSProvider(BaseTTSProvider):
    def __init__(self, config):
        super().__init__(config)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    def synthesize_speech(self, text, voice_id='alloy', **kwargs):
        """Generate speech using OpenAI TTS"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # Validate voice
            valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
            if voice_id not in valid_voices:
                voice_id = 'alloy'
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice_id,
                input=self.validate_text(text),
                response_format="mp3"
            )
            
            # Get audio data
            audio_data = BytesIO()
            for chunk in response.iter_bytes():
                audio_data.write(chunk)
            
            audio_data.seek(0)
            
            return {
                'success': True,
                'audio_data': audio_data.getvalue(),
                'format': 'mp3',
                'voice_used': voice_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_voices(self):
        """Get OpenAI TTS voices"""
        return [
            {'voice_id': 'alloy', 'name': 'Alloy', 'language': 'en-US', 'gender': 'neutral'},
            {'voice_id': 'echo', 'name': 'Echo', 'language': 'en-US', 'gender': 'male'},
            {'voice_id': 'fable', 'name': 'Fable', 'language': 'en-US', 'gender': 'neutral'},
            {'voice_id': 'onyx', 'name': 'Onyx', 'language': 'en-US', 'gender': 'male'},
            {'voice_id': 'nova', 'name': 'Nova', 'language': 'en-US', 'gender': 'female'},
            {'voice_id': 'shimmer', 'name': 'Shimmer', 'language': 'en-US', 'gender': 'female'},
        ]

class ElevenLabsTTSProvider(BaseTTSProvider):
    def __init__(self, config):
        super().__init__(config)
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")
        self.base_url = self.base_url or "https://api.elevenlabs.io/v1"
    
    def synthesize_speech(self, text, voice_id='21m00Tcm4TlvDq8ikWAM', **kwargs):
        """Generate speech using ElevenLabs"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": self.validate_text(text),
                "model_id": kwargs.get('model_id', 'eleven_monolingual_v1'),
                "voice_settings": {
                    "stability": kwargs.get('stability', 0.5),
                    "similarity_boost": kwargs.get('similarity_boost', 0.5),
                    "style": kwargs.get('style', 0.0),
                    "use_speaker_boost": kwargs.get('use_speaker_boost', True)
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            return {
                'success': True,
                'audio_data': response.content,
                'format': 'mp3',
                'voice_used': voice_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_voices(self):
        """Get ElevenLabs voices"""
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            voices_data = response.json()
            voices = []
            
            for voice in voices_data.get('voices', []):
                voices.append({
                    'voice_id': voice['voice_id'],
                    'name': voice['name'],
                    'language': voice.get('labels', {}).get('language', 'en'),
                    'gender': voice.get('labels', {}).get('gender', 'neutral'),
                    'description': voice.get('description', ''),
                    'preview_url': voice.get('preview_url', ''),
                    'is_premium': voice.get('category') == 'premade'
                })
            
            return voices
            
        except Exception as e:
            print(f"Error fetching ElevenLabs voices: {str(e)}")
            # Return default voice if API call fails
            return [
                {'voice_id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Rachel', 'language': 'en', 'gender': 'female'}
            ]

class GoogleTTSProvider(BaseTTSProvider):
    def synthesize_speech(self, text, voice_id='en-US-Wavenet-D', **kwargs):
        """Generate speech using Google TTS (gTTS for simplicity)"""
        try:
            from gtts import gTTS
            import io
            
            # Extract language from voice_id
            language = voice_id.split('-')[0] if '-' in voice_id else 'en'
            
            tts = gTTS(text=self.validate_text(text), lang=language, slow=False)
            
            # Save to BytesIO
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return {
                'success': True,
                'audio_data': audio_buffer.getvalue(),
                'format': 'mp3',
                'voice_used': voice_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_voices(self):
        """Get Google TTS voices (simplified)"""
        return [
            {'voice_id': 'en', 'name': 'English', 'language': 'en-US', 'gender': 'neutral'},
            {'voice_id': 'es', 'name': 'Spanish', 'language': 'es-ES', 'gender': 'neutral'},
            {'voice_id': 'fr', 'name': 'French', 'language': 'fr-FR', 'gender': 'neutral'},
            {'voice_id': 'de', 'name': 'German', 'language': 'de-DE', 'gender': 'neutral'},
            {'voice_id': 'ja', 'name': 'Japanese', 'language': 'ja-JP', 'gender': 'neutral'},
        ]

# 3. tts_factory.py - TTS provider factory
class TTSProviderFactory:
    @staticmethod
    def create_provider(provider_name, config):
        """Create TTS provider instance"""
        
        if provider_name == 'openai':
            return OpenAITTSProvider(config)
        
        elif provider_name == 'elevenlabs':
            return ElevenLabsTTSProvider(config)
        
        elif provider_name == 'google':
            return GoogleTTSProvider(config)
        
        else:
            raise ValueError(f"Unsupported TTS provider: {provider_name}")

# 4. views.py - TTS API endpoints
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json
import time

@method_decorator(csrf_exempt, name='dispatch')
class TextToSpeechView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            provider_name = data.get('provider', 'openai')
            voice_id = data.get('voice_id')
            audio_format = data.get('format', 'mp3')
            
            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)
            
            # Get TTS provider configuration
            try:
                provider_config = TTSProvider.objects.get(name=provider_name, is_active=True)
            except TTSProvider.DoesNotExist:
                return JsonResponse({'error': f'TTS provider {provider_name} not found'}, status=400)
            
            # Create TTS provider instance
            config = {
                'api_key': provider_config.api_key,
                'base_url': provider_config.base_url,
                **provider_config.configuration
            }
            
            tts_provider = TTSProviderFactory.create_provider(provider_name, config)
            
            # Get default voice if not specified
            if not voice_id:
                voices = tts_provider.get_available_voices()
                voice_id = voices[0]['voice_id'] if voices else None
            
            # Record start time
            start_time = time.time()
            
            # Generate speech
            result = tts_provider.synthesize_speech(
                text=text,
                voice_id=voice_id,
                **data.get('voice_settings', {})
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            if not result['success']:
                # Save failed request
                TTSRequest.objects.create(
                    provider=provider_config,
                    text=text,
                    audio_format=audio_format,
                    processing_time_ms=processing_time,
                    success=False,
                    error_message=result['error']
                )
                
                return JsonResponse({'error': result['error']}, status=500)
            
            # Create audio file
            audio_data = result['audio_data']
            audio_file = ContentFile(audio_data)
            audio_filename = f"tts_{int(time.time())}.{result['format']}"
            
            # Save successful request
            tts_request = TTSRequest.objects.create(
                provider=provider_config,
                text=text,
                audio_format=result['format'],
                duration_seconds=None,  # Could be calculated from audio
                file_size_bytes=len(audio_data),
                processing_time_ms=processing_time,
                success=True
            )
            
            tts_request.audio_file.save(audio_filename, audio_file)
            
            return JsonResponse({
                'success': True,
                'audio_url': tts_request.audio_file.url,
                'request_id': str(tts_request.id),
                'provider': provider_name,
                'voice_used': result['voice_used'],
                'format': result['format'],
                'file_size': len(audio_data),
                'processing_time_ms': processing_time
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TTSVoicesView(View):
    def get(self, request, provider_name):
        """Get available voices for a TTS provider"""
        try:
            provider_config = TTSProvider.objects.get(name=provider_name, is_active=True)
            
            # Create provider instance
            config = {
                'api_key': provider_config.api_key,
                'base_url': provider_config.base_url,
                **provider_config.configuration
            }
            
            tts_provider = TTSProviderFactory.create_provider(provider_name, config)
            voices = tts_provider.get_available_voices()
            
            return JsonResponse({
                'provider': provider_name,
                'voices': voices
            })
            
        except TTSProvider.DoesNotExist:
            return JsonResponse({'error': 'TTS provider not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TTSProvidersView(View):
    def get(self, request):
        """Get all available TTS providers"""
        try:
            providers = []
            
            for provider in TTSProvider.objects.filter(is_active=True):
                providers.append({
                    'name': provider.name,
                    'display_name': provider.display_name,
                    'is_default': provider.is_default,
                    'voice_count': provider.voices.count(),
                    'configuration': provider.configuration
                })
            
            return JsonResponse({'providers': providers})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TTSHistoryView(View):
    def get(self, request):
        """Get TTS request history"""
        try:
            requests_list = []
            
            for tts_request in TTSRequest.objects.all().order_by('-created_at')[:20]:
                requests_list.append({
                    'id': str(tts_request.id),
                    'provider': tts_request.provider.name,
                    'text_preview': tts_request.text[:100] + '...' if len(tts_request.text) > 100 else tts_request.text,
                    'audio_url': tts_request.audio_file.url if tts_request.audio_file else None,
                    'success': tts_request.success,
                    'processing_time_ms': tts_request.processing_time_ms,
                    'file_size_bytes': tts_request.file_size_bytes,
                    'created_at': tts_request.created_at.isoformat(),
                    'error_message': tts_request.error_message
                })
            
            return JsonResponse({'requests': requests_list})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 5. urls.py
from django.urls import path
from .views import TextToSpeechView, TTSVoicesView, TTSProvidersView, TTSHistoryView

urlpatterns = [
    path('tts/synthesize/', TextToSpeechView.as_view()),
    path('tts/voices/<str:provider_name>/', TTSVoicesView.as_view()),
    path('tts/providers/', TTSProvidersView.as_view()),
    path('tts/history/', TTSHistoryView.as_view()),
]