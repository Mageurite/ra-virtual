"""
TTS Service Client
Handles text-to-speech synthesis via external services
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
import hashlib
import os
from pathlib import Path

from tts.config import tts_config

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech Service Client"""
    
    def __init__(self):
        self.service_url = tts_config.TTS_SERVICE_URL
        self.cache_enabled = tts_config.ENABLE_CACHE
        
        # Create cache directory if enabled
        if self.cache_enabled:
            Path(tts_config.CACHE_DIR).mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, text: str, engine: str, voice: str) -> str:
        """Generate cache key for TTS request"""
        content = f"{text}:{engine}:{voice}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Retrieve cached audio if available"""
        if not self.cache_enabled:
            return None
        
        cache_file = Path(tts_config.CACHE_DIR) / f"{cache_key}.{tts_config.AUDIO_FORMAT}"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    logger.info(f"Cache hit for key: {cache_key}")
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes):
        """Save audio to cache"""
        if not self.cache_enabled:
            return
        
        cache_file = Path(tts_config.CACHE_DIR) / f"{cache_key}.{tts_config.AUDIO_FORMAT}"
        try:
            with open(cache_file, 'wb') as f:
                f.write(audio_data)
            logger.info(f"Cached audio for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    async def synthesize(
        self,
        text: str,
        engine: Optional[str] = None,
        voice: Optional[str] = None,
        rate: float = 1.0,
        volume: float = 1.0,
        reference_audio: Optional[bytes] = None,
    ) -> bytes:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            engine: TTS engine (edge-tts, cosyvoice, gpt-sovits)
            voice: Voice ID
            rate: Speech rate (0.5 - 2.0)
            volume: Volume (0.0 - 1.0)
            reference_audio: Reference audio for voice cloning (optional)
        
        Returns:
            Audio bytes (WAV format)
        """
        engine = engine or tts_config.DEFAULT_TTS_ENGINE
        voice = voice or tts_config.DEFAULT_VOICE
        
        # Check cache first
        cache_key = self._get_cache_key(text, engine, voice)
        cached_audio = self._get_cached_audio(cache_key)
        if cached_audio:
            return cached_audio
        
        try:
            # Prepare request
            data = {
                "text": text,
                "engine": engine,
                "voice": voice,
                "rate": rate,
                "volume": volume,
            }
            
            files = {}
            if reference_audio:
                files["reference_audio"] = ("audio.wav", reference_audio, "audio/wav")
            
            # Call external TTS service
            async with httpx.AsyncClient(timeout=tts_config.TTS_TIMEOUT) as client:
                if files:
                    response = await client.post(
                        f"{self.service_url}/tts/synthesize",
                        data=data,
                        files=files
                    )
                else:
                    response = await client.post(
                        f"{self.service_url}/tts/synthesize",
                        json=data
                    )
                
                response.raise_for_status()
                audio_data = response.content
                
                # Save to cache
                self._save_to_cache(cache_key, audio_data)
                
                logger.info(f"Synthesized {len(audio_data)} bytes for text: {text[:50]}...")
                return audio_data
                
        except httpx.TimeoutException:
            logger.error(f"TTS timeout for engine: {engine}")
            raise Exception("TTS synthesis timeout")
        except httpx.HTTPError as e:
            logger.error(f"TTS HTTP error: {e}")
            raise Exception(f"TTS synthesis failed: {str(e)}")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    async def get_available_voices(self, engine: Optional[str] = None) -> List[dict]:
        """
        Get available voices for a specific engine
        
        Args:
            engine: TTS engine name (if None, returns all)
        
        Returns:
            List of voice info dicts
        """
        try:
            # Try to get from external service first
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.service_url}/tts/voices",
                    params={"engine": engine} if engine else {}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("voices", [])
        except Exception as e:
            logger.warning(f"Failed to get voices from service: {e}")
        
        # Fallback to local config
        if engine:
            return tts_config.get_voices_for_engine(engine)
        
        # Return all voices
        all_voices = []
        for eng in tts_config.AVAILABLE_ENGINES:
            voices = tts_config.get_voices_for_engine(eng)
            for voice in voices:
                voice["engine"] = eng
            all_voices.extend(voices)
        return all_voices
    
    async def get_available_engines(self) -> List[dict]:
        """
        Get list of available TTS engines
        
        Returns:
            List of engine info dicts
        """
        engines = [
            {
                "id": "edge-tts",
                "name": "Microsoft Edge TTS",
                "description": "Free online TTS service with high quality",
                "requires_reference": False,
            },
            {
                "id": "cosyvoice",
                "name": "CosyVoice",
                "description": "High-quality local TTS model",
                "requires_reference": False,
            },
            {
                "id": "gpt-sovits",
                "name": "GPT-SoVITS",
                "description": "Voice cloning TTS with custom voice",
                "requires_reference": True,
            },
        ]
        
        # Check which engines are actually available
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.service_url}/tts/engines")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("engines", engines)
        except Exception as e:
            logger.warning(f"Failed to get engines from service: {e}")
        
        return engines
    
    async def clone_voice(
        self,
        reference_audio: bytes,
        text: str,
        voice_name: Optional[str] = None,
    ) -> bytes:
        """
        Clone voice from reference audio and synthesize text
        
        Args:
            reference_audio: Reference audio bytes
            text: Text to synthesize
            voice_name: Optional name for the cloned voice
        
        Returns:
            Synthesized audio bytes
        """
        try:
            files = {
                "reference_audio": ("audio.wav", reference_audio, "audio/wav")
            }
            data = {
                "text": text,
                "voice_name": voice_name or "custom"
            }
            
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.service_url}/tts/clone",
                    data=data,
                    files=files
                )
                response.raise_for_status()
                return response.content
                
        except Exception as e:
            logger.error(f"Voice cloning error: {e}")
            raise Exception(f"Voice cloning failed: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check TTS service health
        
        Returns:
            Health status dict
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.service_url}/health")
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "service_url": self.service_url,
                        "engines": tts_config.AVAILABLE_ENGINES
                    }
        except Exception as e:
            logger.error(f"TTS health check failed: {e}")
        
        return {
            "status": "unhealthy",
            "service_url": self.service_url,
            "error": "Service unavailable"
        }


# Singleton instance
_tts_service_instance = None


def get_tts_service() -> TTSService:
    """Get or create TTS service instance"""
    global _tts_service_instance
    if _tts_service_instance is None:
        _tts_service_instance = TTSService()
    return _tts_service_instance
