import json
import base64
import os
from typing import Dict, Any, Optional
from django.conf import settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Model registry to manage model configurations from MODEL_LIST.MD"""
    
    def __init__(self):
        self.models = {
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
    
    def get_default_model(self, category: str) -> str:
        """Get the default model for a category"""
        return self.models.get(category, {}).get("default", "")
    
    def is_valid_model(self, category: str, model: str) -> bool:
        """Check if a model is valid for a category"""
        return model in self.models.get(category, {}).get("models", [])
    
    def get_model(self, category: str, model: Optional[str] = None) -> str:
        """Get model for category, with fallback to default if invalid"""
        if model and self.is_valid_model(category, model):
            return model
        return self.get_default_model(category)


class OpenAIClient:
    """OpenAI client wrapper for STT, LLM, and TTS"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model_registry = ModelRegistry()
    
    def speech_to_text(self, audio_file, model: Optional[str] = None) -> Dict[str, Any]:
        """Convert speech to text using OpenAI Whisper"""
        try:
            model = self.model_registry.get_model("stt", model)
            
            transcript = self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                temperature=0
            )
            
            return {
                "transcript": transcript.text,
                "model_used": model,
                "success": True
            }
        except Exception as e:
            logger.error(f"STT error: {str(e)}")
            return {
                "transcript": "",
                "model_used": model or self.model_registry.get_default_model("stt"),
                "success": False,
                "error": str(e)
            }
    
    def text_to_text(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate text response using OpenAI LLM"""
        try:
            model = self.model_registry.get_model("text_gen", model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": text}
                ],
                temperature=0.7
            )
            
            return {
                "text_response": response.choices[0].message.content,
                "model_used": model,
                "success": True
            }
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return {
                "text_response": "",
                "model_used": model or self.model_registry.get_default_model("text_gen"),
                "success": False,
                "error": str(e)
            }
    
    def text_to_speech(self, text: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            model = self.model_registry.get_model("tts", model)
            
            response = self.client.audio.speech.create(
                model=model,
                voice="alloy",
                input=text
            )
            
            # Convert to base64
            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "audio": audio_base64,
                "model_used": model,
                "success": True
            }
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
            return {
                "audio": "",
                "model_used": model or self.model_registry.get_default_model("tts"),
                "success": False,
                "error": str(e)
            }


class ConversationService:
    """Service to handle the complete STT → LLM → TTS pipeline"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.openai_client = OpenAIClient(api_key, base_url)
    
    def process_conversation(self, audio_file, stt_model: Optional[str] = None, 
                           text_model: Optional[str] = None, 
                           tts_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process the complete conversation pipeline:
        1. STT: Convert audio to text
        2. LLM: Generate text response
        3. TTS: Convert response to audio
        """
        result = {
            "transcript": "",
            "text_response": "",
            "audio": "",
            "models_used": {},
            "success": False,
            "errors": []
        }
        
        try:
            # Step 1: Speech to Text
            stt_result = self.openai_client.speech_to_text(audio_file, stt_model)
            result["transcript"] = stt_result["transcript"]
            result["models_used"]["stt"] = stt_result["model_used"]
            
            if not stt_result["success"]:
                result["errors"].append(f"STT error: {stt_result.get('error', 'Unknown error')}")
                return result
            
            # Step 2: Text to Text (LLM)
            llm_result = self.openai_client.text_to_text(stt_result["transcript"], text_model)
            result["text_response"] = llm_result["text_response"]
            result["models_used"]["text"] = llm_result["model_used"]
            
            if not llm_result["success"]:
                result["errors"].append(f"LLM error: {llm_result.get('error', 'Unknown error')}")
                return result
            
            # Step 3: Text to Speech
            tts_result = self.openai_client.text_to_speech(llm_result["text_response"], tts_model)
            result["audio"] = tts_result["audio"]
            result["models_used"]["tts"] = tts_result["model_used"]
            
            if not tts_result["success"]:
                result["errors"].append(f"TTS error: {tts_result.get('error', 'Unknown error')}")
                return result
            
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Conversation processing error: {str(e)}")
            result["errors"].append(f"Processing error: {str(e)}")
        
        return result