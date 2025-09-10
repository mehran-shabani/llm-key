import base64
import logging
from typing import Dict, Any, Optional
from core.openai_client import openai_client
from core.model_registry import model_registry

logger = logging.getLogger(__name__)


class ConversationService:
    """Service to handle the complete STT → LLM → TTS pipeline"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.model_registry = model_registry
    
    def process_conversation(self, audio_file, stt_model: Optional[str] = None, 
                           text_model: Optional[str] = None, 
                           tts_model: Optional[str] = None,
                           headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
            stt_result = self._speech_to_text(audio_file, stt_model, headers)
            result["transcript"] = stt_result["transcript"]
            result["models_used"]["stt"] = stt_result["model_used"]
            
            if not stt_result["success"]:
                result["errors"].append(f"STT error: {stt_result.get('error', 'Unknown error')}")
                return result
            
            # Step 2: Text to Text (LLM)
            llm_result = self._text_to_text(stt_result["transcript"], text_model, headers)
            result["text_response"] = llm_result["text_response"]
            result["models_used"]["text"] = llm_result["model_used"]
            
            if not llm_result["success"]:
                result["errors"].append(f"LLM error: {llm_result.get('error', 'Unknown error')}")
                return result
            
            # Step 3: Text to Speech
            tts_result = self._text_to_speech(llm_result["text_response"], tts_model, headers)
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
    
    def _speech_to_text(self, audio_file, model: Optional[str] = None, 
                       headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Convert speech to text using OpenAI Whisper"""
        try:
            model = self.model_registry.select("stt", model)
            client = self.openai_client._get_client(headers)
            
            transcript = client.audio.transcriptions.create(
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
    
    def _text_to_text(self, text: str, model: Optional[str] = None,
                     headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate text response using OpenAI LLM"""
        try:
            model = self.model_registry.select("text_gen", model)
            
            response = self.openai_client.generate_text(
                model=model,
                messages=[{"role": "user", "content": text}],
                temperature=0.7,
                headers=headers
            )
            
            return {
                "text_response": response["content"],
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
    
    def _text_to_speech(self, text: str, model: Optional[str] = None,
                       headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            model = self.model_registry.select("tts", model)
            client = self.openai_client._get_client(headers)
            
            response = client.audio.speech.create(
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