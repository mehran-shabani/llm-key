"""
OpenAI client utility for making API calls
"""

import os
import requests
from typing import Dict, Any, Optional, Union
from django.conf import settings


class OpenAIClient:
    """Client for OpenAI API calls"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (if None, will use from settings or env)
            base_url: OpenAI API base URL (if None, will use from settings or env)
        """
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
        self.base_url = base_url or getattr(settings, 'OPENAI_BASE_URL', None) or os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Make HTTP request to OpenAI API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request data
            headers: Additional headers
            
        Returns:
            Response JSON data
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"OpenAI API request failed: {e}")
    
    def chat_completion(self, messages: list, model: str = "gpt-4o", **kwargs) -> Dict[str, Any]:
        """
        Create a chat completion
        
        Args:
            messages: List of message objects
            model: Model to use
            **kwargs: Additional parameters for the API call
            
        Returns:
            API response
        """
        data = {
            'model': model,
            'messages': messages,
            **kwargs
        }
        return self._make_request('POST', '/chat/completions', data)
    
    def text_completion(self, prompt: str, model: str = "gpt-4o", **kwargs) -> Dict[str, Any]:
        """
        Create a text completion
        
        Args:
            prompt: Text prompt
            model: Model to use
            **kwargs: Additional parameters for the API call
            
        Returns:
            API response
        """
        data = {
            'model': model,
            'prompt': prompt,
            **kwargs
        }
        return self._make_request('POST', '/completions', data)
    
    def embeddings(self, input_text: Union[str, list], model: str = "text-embedding-3-small") -> Dict[str, Any]:
        """
        Create embeddings
        
        Args:
            input_text: Text or list of texts to embed
            model: Embedding model to use
            
        Returns:
            API response
        """
        data = {
            'model': model,
            'input': input_text
        }
        return self._make_request('POST', '/embeddings', data)
    
    def image_generation(self, prompt: str, model: str = "dall-e-3", **kwargs) -> Dict[str, Any]:
        """
        Generate images
        
        Args:
            prompt: Image generation prompt
            model: Image generation model
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        data = {
            'model': model,
            'prompt': prompt,
            **kwargs
        }
        return self._make_request('POST', '/images/generations', data)
    
    def text_to_speech(self, text: str, model: str = "tts-1", voice: str = "alloy", **kwargs) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            model: TTS model
            voice: Voice to use
            **kwargs: Additional parameters
            
        Returns:
            Audio data as bytes
        """
        data = {
            'model': model,
            'input': text,
            'voice': voice,
            **kwargs
        }
        
        url = f"{self.base_url.rstrip('/')}/audio/speech"
        headers = self._get_headers()
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content
    
    def speech_to_text(self, audio_file: bytes, model: str = "whisper-1", **kwargs) -> Dict[str, Any]:
        """
        Convert speech to text
        
        Args:
            audio_file: Audio file data
            model: STT model
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        url = f"{self.base_url.rstrip('/')}/audio/transcriptions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        
        files = {
            'file': ('audio.mp3', audio_file, 'audio/mpeg'),
            'model': (None, model),
        }
        
        # Add additional parameters
        for key, value in kwargs.items():
            files[key] = (None, str(value))
        
        response = requests.post(url, files=files, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()


def get_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAIClient:
    """
    Get OpenAI client instance
    
    Args:
        api_key: Optional API key override
        base_url: Optional base URL override
        
    Returns:
        OpenAIClient instance
    """
    return OpenAIClient(api_key=api_key, base_url=base_url)