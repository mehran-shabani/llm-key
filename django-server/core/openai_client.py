import os
import openai
from typing import Dict, Any, Optional


class OpenAIClient:
    """OpenAI client with support for custom base URL and API key."""
    
    def __init__(self):
        self._client = None
        self._base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self._api_key = os.getenv('OPENAI_API_KEY')
    
    def _get_client(self, headers: Optional[Dict[str, str]] = None) -> openai.OpenAI:
        """Get OpenAI client with optional header overrides."""
        # Extract custom headers if provided
        base_url = self._base_url
        api_key = self._api_key
        
        if headers:
            if 'X-OpenAI-Base-URL' in headers:
                base_url = headers['X-OpenAI-Base-URL']
            if 'X-OpenAI-Key' in headers:
                api_key = headers['X-OpenAI-Key']
        
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        return openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def generate_text(self, model: str, messages: list, **kwargs) -> Dict[str, Any]:
        """Generate text using chat completions."""
        client = self._get_client(kwargs.get('headers'))
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **{k: v for k, v in kwargs.items() if k != 'headers'}
        )
        
        return {
            'content': response.choices[0].message.content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
        }
    
    def generate_embedding(self, model: str, input_text: str, **kwargs) -> Dict[str, Any]:
        """Generate embedding for input text."""
        client = self._get_client(kwargs.get('headers'))
        
        response = client.embeddings.create(
            model=model,
            input=input_text,
            **{k: v for k, v in kwargs.items() if k != 'headers'}
        )
        
        return {
            'embedding': response.data[0].embedding,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'total_tokens': response.usage.total_tokens
            } if response.usage else None
        }
    
    def generate_image(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate image from text prompt."""
        client = self._get_client(kwargs.get('headers'))
        
        response = client.images.generate(
            model=model,
            prompt=prompt,
            **{k: v for k, v in kwargs.items() if k != 'headers'}
        )
        
        return {
            'url': response.data[0].url,
            'revised_prompt': response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None
        }


# Global instance
openai_client = OpenAIClient()