"""
TTS (Text-to-Speech) Module
Provides text-to-speech synthesis services
"""
from .config import TTSConfig, tts_config
from .service import TTSService, get_tts_service

__all__ = [
    'TTSConfig',
    'tts_config',
    'TTSService',
    'get_tts_service',
]
