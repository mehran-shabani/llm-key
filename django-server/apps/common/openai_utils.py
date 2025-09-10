"""
OpenAI-specific utilities for Django applications.
Contains OpenAI LLM and embedding providers.
"""

import os
from typing import Any, Dict, List, Optional, Union

from django.conf import settings


class OpenAIClient:
    """OpenAI API client wrapper."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to OPEN_AI_KEY from settings)
        """
        self.api_key = api_key or getattr(settings, 'OPEN_AI_KEY', os.getenv('OPEN_AI_KEY'))
        if not self.api_key:
            raise ValueError("No OpenAI API key was set.")
        
        # Note: In a real implementation, you would import and use the OpenAI Python library
        # import openai
        # self.client = openai.OpenAI(api_key=self.api_key)
        self.client = None  # Placeholder for actual OpenAI client
    
    def log(self, text: str, *args: Any) -> None:
        """Log message with OpenAI prefix."""
        print(f"[OpenAI] {text}", *args)


class OpenAiLLM:
    """OpenAI LLM provider for chat completions."""
    
    def __init__(self, embedder: Optional[Any] = None, model_preference: Optional[str] = None):
        """
        Initialize OpenAI LLM provider.
        
        Args:
            embedder: Embedding provider instance
            model_preference: Preferred model name
        """
        self.openai = OpenAIClient()
        self.model = model_preference or getattr(settings, 'OPEN_MODEL_PREF', 'gpt-4o')
        self.embedder = embedder
        self.default_temp = 0.7
        
        # Model limits (simplified)
        self.limits = {
            'history': 4096 * 0.15,
            'system': 4096 * 0.15,
            'user': 4096 * 0.7,
        }
        
        self.log(f"Initialized {self.model} with context window {self.prompt_window_limit()}")
    
    def log(self, text: str, *args: Any) -> None:
        """Log message with LLM prefix."""
        print(f"[OpenAiLLM] {text}", *args)
    
    @property
    def is_o_type_model(self) -> bool:
        """Check if the model is an o1 model."""
        return self.model.startswith('o')
    
    def streaming_enabled(self) -> bool:
        """Check if streaming is enabled for this model."""
        # o3-mini is the only o-type model that supports streaming
        if self.is_o_type_model and self.model != 'o3-mini':
            return False
        return True
    
    @staticmethod
    def prompt_window_limit(model_name: str) -> int:
        """Get prompt window limit for a model."""
        # Simplified model limits
        limits = {
            'gpt-4o': 128000,
            'gpt-4o-mini': 128000,
            'gpt-4': 8192,
            'gpt-3.5-turbo': 4096,
            'o1-preview': 128000,
            'o1-mini': 128000,
        }
        return limits.get(model_name, 4096)
    
    def prompt_window_limit(self) -> int:
        """Get prompt window limit for current model."""
        return self.prompt_window_limit(self.model)
    
    async def is_valid_chat_completion_model(self, model_name: str = "") -> bool:
        """
        Check if model is valid for chat completion.
        
        Args:
            model_name: Model name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Simplified validation - in real implementation would check OpenAI API
        is_preset = (
            model_name.lower().includes('gpt') or 
            model_name.lower().startswith('o')
        )
        return is_preset
    
    def construct_prompt(self, system_prompt: str = "", context_texts: List[str] = None,
                        chat_history: List[Dict] = None, user_prompt: str = "",
                        attachments: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Construct prompt for OpenAI API.
        
        Args:
            system_prompt: System prompt text
            context_texts: List of context texts
            chat_history: List of chat history messages
            user_prompt: User prompt text
            attachments: List of attachments
            
        Returns:
            List of message dictionaries
        """
        if context_texts is None:
            context_texts = []
        if chat_history is None:
            chat_history = []
        if attachments is None:
            attachments = []
        
        # Append context to system prompt
        if context_texts:
            context_text = "\nContext:\n" + "\n".join([
                f"[CONTEXT {i}]:\n{text}\n[END CONTEXT {i}]\n"
                for i, text in enumerate(context_texts)
            ])
            system_prompt += context_text
        
        # o1 Models do not support the "system" role
        prompt = {
            'role': 'user' if self.is_o_type_model else 'system',
            'content': system_prompt
        }
        
        messages = [prompt]
        
        # Add chat history
        for msg in chat_history:
            messages.append(msg)
        
        # Add user message with attachments
        content = self._generate_content(user_prompt, attachments)
        messages.append({
            'role': 'user',
            'content': content
        })
        
        return messages
    
    def _generate_content(self, user_prompt: str, attachments: List[Dict]) -> Union[str, List[Dict]]:
        """Generate content array for message with attachments."""
        if not attachments:
            return user_prompt
        
        content = [{'type': 'text', 'text': user_prompt}]
        for attachment in attachments:
            content.append({
                'type': 'image_url',
                'image_url': {
                    'url': attachment.get('contentString', ''),
                    'detail': 'auto'
                }
            })
        return content
    
    async def get_chat_completion(self, messages: List[Dict] = None, 
                                temperature: float = 0.7) -> Dict[str, Any]:
        """
        Get chat completion from OpenAI.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Returns:
            Dictionary with text response and metrics
        """
        if not messages:
            messages = []
        
        if not await self.is_valid_chat_completion_model(self.model):
            raise ValueError(f"OpenAI chat: {self.model} is not valid for chat completion!")
        
        # Note: In real implementation, this would call the OpenAI API
        # For now, return a mock response
        return {
            'textResponse': 'Mock response from OpenAI',
            'metrics': {
                'prompt_tokens': 100,
                'completion_tokens': 50,
                'total_tokens': 150,
                'outputTps': 25.0,
                'duration': 2.0
            }
        }
    
    async def embed_text_input(self, text_input: Union[str, List[str]]) -> List[float]:
        """Embed text input using the embedder."""
        if self.embedder:
            return await self.embedder.embed_text_input(text_input)
        return []
    
    async def embed_chunks(self, text_chunks: List[str]) -> List[List[float]]:
        """Embed text chunks using the embedder."""
        if self.embedder:
            return await self.embedder.embed_chunks(text_chunks)
        return []


class OpenAiEmbedder:
    """OpenAI embedding provider."""
    
    def __init__(self):
        """Initialize OpenAI embedder."""
        self.openai = OpenAIClient()
        self.model = getattr(settings, 'EMBEDDING_MODEL_PREF', 'text-embedding-ada-002')
        self.max_concurrent_chunks = 500
        self.embedding_max_chunk_length = 8191
        
        self.log("OpenAI Embedder initialized")
    
    def log(self, text: str, *args: Any) -> None:
        """Log message with embedder prefix."""
        print(f"[OpenAiEmbedder] {text}", *args)
    
    async def embed_text_input(self, text_input: Union[str, List[str]]) -> List[float]:
        """
        Embed text input.
        
        Args:
            text_input: Text or list of texts to embed
            
        Returns:
            Embedding vector
        """
        if isinstance(text_input, str):
            text_input = [text_input]
        
        result = await self.embed_chunks(text_input)
        return result[0] if result else []
    
    async def embed_chunks(self, text_chunks: List[str]) -> List[List[float]]:
        """
        Embed text chunks.
        
        Args:
            text_chunks: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        self.log(f"Embedding {len(text_chunks)} chunks...")
        
        # Note: In real implementation, this would call the OpenAI embeddings API
        # For now, return mock embeddings
        mock_embeddings = []
        for chunk in text_chunks:
            # Generate mock embedding vector (1536 dimensions for text-embedding-ada-002)
            mock_embedding = [0.1] * 1536
            mock_embeddings.append(mock_embedding)
        
        return mock_embeddings