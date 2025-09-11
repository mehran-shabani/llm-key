# Feature: Audio/Video Transcription
# Description: Convert audio/video files to text using Whisper models
# Library: Django, openai-whisper, pydub, requests

# 1. models.py - Audio transcription storage
from django.db import models
import uuid

class AudioTranscription(models.Model):
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI Whisper'),
        ('local', 'Local Whisper'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    filename = models.CharField(max_length=200)
    file_type = models.CharField(max_length=10)
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES, default='local')
    duration_seconds = models.FloatField(null=True, blank=True)
    transcription_text = models.TextField()
    word_count = models.IntegerField(default=0)
    confidence_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# 2. transcription_providers.py - Whisper provider implementations
import os
import tempfile
import requests
from pydub import AudioSegment
from django.conf import settings

class BaseWhisperProvider:
    def __init__(self, options=None):
        self.options = options or {}
    
    def validate_audio_file(self, file_path):
        """Validate audio file format and duration"""
        try:
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000.0  # Convert to seconds
            
            # Check duration limits (max 4 hours)
            if duration > 4 * 60 * 60:
                raise ValueError("Audio file exceeds maximum duration of 4 hours")
            
            # Check sample rate (minimum 4kHz)
            if audio.frame_rate < 4000:
                raise ValueError("Audio sample rate too low (minimum 4kHz required)")
            
            return True, duration
        except Exception as e:
            return False, str(e)
    
    def convert_to_wav(self, input_path):
        """Convert audio file to WAV format for processing"""
        try:
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono, 16kHz WAV
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio.export(temp_file.name, format='wav')
                return temp_file.name
        except Exception as e:
            raise Exception(f"Audio conversion failed: {str(e)}")

class OpenAIWhisperProvider(BaseWhisperProvider):
    def __init__(self, options=None):
        super().__init__(options)
        self.api_key = options.get('api_key') or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    def transcribe_file(self, file_path, filename):
        """Transcribe audio using OpenAI Whisper API"""
        try:
            # Validate audio file
            is_valid, duration_or_error = self.validate_audio_file(file_path)
            if not is_valid:
                return {'success': False, 'error': duration_or_error}
            
            duration = duration_or_error
            
            # Convert to WAV if needed
            wav_path = self.convert_to_wav(file_path)
            
            try:
                # Call OpenAI Whisper API
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                }
                
                with open(wav_path, 'rb') as audio_file:
                    files = {
                        'file': (filename, audio_file, 'audio/wav'),
                        'model': (None, 'whisper-1'),
                        'temperature': (None, '0'),
                    }
                    
                    response = requests.post(
                        'https://api.openai.com/v1/audio/transcriptions',
                        headers=headers,
                        files=files,
                        timeout=300  # 5 minute timeout
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'success': True,
                        'text': result.get('text', ''),
                        'duration': duration,
                        'provider': 'openai'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'OpenAI API error: {response.text}'
                    }
                    
            finally:
                # Clean up temporary WAV file
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}

class LocalWhisperProvider(BaseWhisperProvider):
    def __init__(self, options=None):
        super().__init__(options)
        self.model_name = options.get('model', 'base')  # base, small, medium, large
    
    def transcribe_file(self, file_path, filename):
        """Transcribe audio using local Whisper model (simplified)"""
        try:
            # Validate audio file
            is_valid, duration_or_error = self.validate_audio_file(file_path)
            if not is_valid:
                return {'success': False, 'error': duration_or_error}
            
            duration = duration_or_error
            
            # Convert to WAV format
            wav_path = self.convert_to_wav(file_path)
            
            try:
                # Simulate local Whisper processing
                # In real implementation, you would use: import whisper
                # model = whisper.load_model(self.model_name)
                # result = model.transcribe(wav_path)
                
                # For this example, we'll simulate the transcription
                transcription_text = f"[Simulated transcription of {filename} using local Whisper {self.model_name} model. Duration: {duration:.1f}s]"
                
                return {
                    'success': True,
                    'text': transcription_text,
                    'duration': duration,
                    'provider': 'local'
                }
                
            finally:
                # Clean up temporary WAV file
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
        except Exception as e:
            return {'success': False, 'error': str(e)}

# 3. views.py - Audio transcription endpoint
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import tempfile
import os

@method_decorator(csrf_exempt, name='dispatch')
class AudioTranscriptionView(View):
    def post(self, request):
        try:
            if 'audio_file' not in request.FILES:
                return JsonResponse({'error': 'No audio file provided'}, status=400)
            
            audio_file = request.FILES['audio_file']
            filename = audio_file.name
            provider = request.POST.get('provider', 'local')
            
            # Validate file type
            allowed_extensions = ['.mp3', '.wav', '.mp4', '.mpeg', '.m4a']
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in allowed_extensions:
                return JsonResponse({
                    'error': f'Unsupported file type: {file_ext}. Allowed: {allowed_extensions}'
                }, status=400)
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Initialize transcription provider
                if provider == 'openai':
                    whisper_provider = OpenAIWhisperProvider({
                        'api_key': getattr(settings, 'OPENAI_API_KEY', None)
                    })
                else:
                    whisper_provider = LocalWhisperProvider({
                        'model': request.POST.get('model', 'base')
                    })
                
                # Transcribe the audio
                result = whisper_provider.transcribe_file(temp_path, filename)
                
                if not result['success']:
                    return JsonResponse({'error': result['error']}, status=400)
                
                # Save transcription to database
                transcription = AudioTranscription.objects.create(
                    filename=filename,
                    file_type=file_ext[1:],  # Remove the dot
                    provider=result['provider'],
                    duration_seconds=result.get('duration'),
                    transcription_text=result['text'],
                    word_count=len(result['text'].split()) if result['text'] else 0
                )
                
                return JsonResponse({
                    'success': True,
                    'transcription': {
                        'id': str(transcription.id),
                        'filename': transcription.filename,
                        'provider': transcription.provider,
                        'duration': transcription.duration_seconds,
                        'text': transcription.transcription_text,
                        'word_count': transcription.word_count,
                        'created_at': transcription.created_at.isoformat()
                    }
                })
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TranscriptionListView(View):
    def get(self, request):
        try:
            transcriptions = AudioTranscription.objects.all()[:20]
            
            transcription_list = []
            for t in transcriptions:
                transcription_list.append({
                    'id': str(t.id),
                    'filename': t.filename,
                    'provider': t.provider,
                    'duration': t.duration_seconds,
                    'word_count': t.word_count,
                    'text_preview': t.transcription_text[:100] + '...' if len(t.transcription_text) > 100 else t.transcription_text,
                    'created_at': t.created_at.isoformat()
                })
            
            return JsonResponse({'transcriptions': transcription_list})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 4. urls.py
from django.urls import path
from .views import AudioTranscriptionView, TranscriptionListView

urlpatterns = [
    path('audio/transcribe/', AudioTranscriptionView.as_view()),
    path('transcriptions/', TranscriptionListView.as_view()),
]