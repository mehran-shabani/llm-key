import json
import os
from typing import Dict, List, Optional


class ModelRegistry:
    """Registry for managing OpenAI models by category."""
    
    def __init__(self):
        self._models = self._load_models()
    
    def _load_models(self) -> Dict[str, Dict[str, any]]:
        """Load models from MODEL_LIST.md file."""
        model_list_path = os.path.join(os.path.dirname(__file__), '..', 'MODEL_LIST.MD')
        
        try:
            with open(model_list_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract the first JSON block from the markdown file
            start_idx = content.find('```json')
            if start_idx == -1:
                raise ValueError("No JSON block found in MODEL_LIST.MD")
            
            end_idx = content.find('```', start_idx + 7)
            if end_idx == -1:
                raise ValueError("No closing ``` found in MODEL_LIST.MD")
            
            json_content = content[start_idx + 7:end_idx].strip()
            return json.loads(json_content)
            
        except Exception as e:
            # Fallback to default models if file reading fails
            return {
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
    
    def get_models(self, category: str) -> List[str]:
        """Get list of available models for a category."""
        return self._models.get(category, {}).get("models", [])
    
    def get_default_model(self, category: str) -> str:
        """Get default model for a category."""
        return self._models.get(category, {}).get("default", "")
    
    def select(self, category: str, requested: Optional[str] = None) -> str:
        """Select model for a category, using requested model if valid, otherwise default."""
        available_models = self.get_models(category)
        
        if requested and requested in available_models:
            return requested
        
        default_model = self.get_default_model(category)
        if default_model:
            return default_model
        
        # Fallback to first available model
        if available_models:
            return available_models[0]
        
        raise ValueError(f"No models available for category: {category}")


# Global instance
model_registry = ModelRegistry()