"""
TTS Service Configuration
Text-to-Speech configuration management
"""
import os
from typing import List, Optional


class TTSConfig:
    """TTS Service Configuration"""
    
    # External TTS Service URL (Mageurite)
    TTS_SERVICE_URL: str = os.getenv("TTS_SERVICE_URL", "http://localhost:8604")
    
    # Timeouts
    TTS_TIMEOUT: int = int(os.getenv("TTS_TIMEOUT", "60"))
    
    # Default TTS Settings
    DEFAULT_TTS_ENGINE: str = os.getenv("DEFAULT_TTS_ENGINE", "edge-tts")
    DEFAULT_VOICE: str = os.getenv("DEFAULT_VOICE", "zh-CN-XiaoxiaoNeural")
    DEFAULT_RATE: float = float(os.getenv("DEFAULT_RATE", "1.0"))
    DEFAULT_VOLUME: float = float(os.getenv("DEFAULT_VOLUME", "1.0"))
    
    # Available TTS Engines
    AVAILABLE_ENGINES: List[str] = [
        "edge-tts",      # Microsoft Edge TTS (free, online)
        "cosyvoice",     # CosyVoice (high quality, local)
        "gpt-sovits",    # GPT-SoVITS (voice cloning)
    ]
    
    # Voice Options per Engine
    EDGE_TTS_VOICES: List[dict] = [
        {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声)", "lang": "zh-CN"},
        {"id": "zh-CN-YunxiNeural", "name": "云希 (男声)", "lang": "zh-CN"},
        {"id": "zh-CN-YunyangNeural", "name": "云扬 (男声)", "lang": "zh-CN"},
        {"id": "en-US-JennyNeural", "name": "Jenny (Female)", "lang": "en-US"},
        {"id": "en-US-GuyNeural", "name": "Guy (Male)", "lang": "en-US"},
    ]
    
    # Audio Format
    AUDIO_FORMAT: str = os.getenv("AUDIO_FORMAT", "wav")
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    
    # Cache Settings
    ENABLE_CACHE: bool = os.getenv("TTS_ENABLE_CACHE", "true").lower() == "true"
    CACHE_DIR: str = os.getenv("TTS_CACHE_DIR", "/tmp/tts_cache")
    
    @classmethod
    def validate_service(cls) -> bool:
        """Validate TTS service is available"""
        try:
            import httpx
            response = httpx.get(f"{cls.TTS_SERVICE_URL}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"TTS service validation failed: {e}")
            return False
    
    @classmethod
    def get_voices_for_engine(cls, engine: str) -> List[dict]:
        """Get available voices for a specific engine"""
        if engine == "edge-tts":
            return cls.EDGE_TTS_VOICES
        elif engine == "cosyvoice":
            return [
                {"id": "default", "name": "默认音色", "lang": "zh-CN"},
                {"id": "female", "name": "女声", "lang": "zh-CN"},
                {"id": "male", "name": "男声", "lang": "zh-CN"},
            ]
        elif engine == "gpt-sovits":
            return [
                {"id": "custom", "name": "自定义克隆音色", "lang": "multi"},
            ]
        return []


# Global config instance
tts_config = TTSConfig()
