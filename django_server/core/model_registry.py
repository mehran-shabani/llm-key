"""
Model registry for managing OpenAI models from MODEL_LIST.md
"""

import os
from typing import Dict, List, Optional, Any
from django.conf import settings
from .md_parser import extract_first_json_block


class ModelRegistry:
    """Registry for OpenAI models loaded from MODEL_LIST.md"""
    
    def __init__(self):
        self._models = None
        self._load_models()
    
    def _load_models(self) -> None:
        """Load models from MODEL_LIST.md file"""
        model_list_path = getattr(settings, 'MODEL_LIST_PATH', None)
        if not model_list_path:
            # Fallback to default path
            model_list_path = os.path.join(os.path.dirname(__file__), '..', 'MODEL_LIST.md')
        
        if os.path.exists(model_list_path):
            self._models = extract_first_json_block(model_list_path)
        else:
            # Fallback models if file doesn't exist
            self._models = {
                "text_gen": {
                    "default": "gpt-4o",
                    "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"]
                },
                "text2text": {
                    "default": "gpt-4o-mini",
                    "models": ["gpt-4o-mini", "gpt-4.1-mini"]
                },
                "image": {
                    "default": "gpt-image-1",
                    "models": ["gpt-image-1"]
                },
                "embedding": {
                    "default": "text-embedding-3-small",
                    "models": ["text-embedding-3-small", "text-embedding-3-large"]
                },
                "tts": {
                    "default": "tts-1",
                    "models": ["tts-1", "tts-1-hd"]
                },
                "stt": {
                    "default": "whisper-1",
                    "models": ["whisper-1"]
                }
            }
    
    def get_categories(self) -> List[str]:
        """Get all available model categories"""
        if not self._models:
            return []
        return list(self._models.keys())
    
    def get_models(self, category: str) -> List[str]:
        """Get all models for a specific category"""
        if not self._models or category not in self._models:
            return []
        return self._models[category].get('models', [])
    
    def get_default_model(self, category: str) -> Optional[str]:
        """Get the default model for a specific category"""
        if not self._models or category not in self._models:
            return None
        return self._models[category].get('default')
    
    def select(self, category: str, requested: Optional[str] = None) -> Optional[str]:
        """
        Select a model for a category.
        
        Args:
            category: Model category (e.g., 'text_gen', 'embedding')
            requested: Specific model name requested, or None for default
            
        Returns:
            Selected model name, or None if not found
        """
        if not self._models or category not in self._models:
            return None
        
        available_models = self.get_models(category)
        
        if requested and requested in available_models:
            return requested
        
        return self.get_default_model(category)
    
    def is_valid_model(self, category: str, model: str) -> bool:
        """Check if a model is valid for a category"""
        return model in self.get_models(category)


# Global instance
model_registry = ModelRegistry()