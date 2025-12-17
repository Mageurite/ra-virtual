"""
Avatar Service Configuration
Manages avatar and lip-sync service settings
"""
import os
from pathlib import Path


class AvatarConfig:
    """Avatar/Lip-Sync Service Configuration"""
    
    # Service URLs
    LIPSYNC_SERVICE_URL: str = os.getenv("LIPSYNC_SERVICE_URL", "http://localhost:8615")
    TTS_SERVICE_URL: str = os.getenv("TTS_SERVICE_URL", "http://localhost:8604")
    
    # Timeouts
    AVATAR_CREATE_TIMEOUT: int = int(os.getenv("AVATAR_CREATE_TIMEOUT", "200"))  # seconds
    AVATAR_START_TIMEOUT: int = int(os.getenv("AVATAR_START_TIMEOUT", "300"))    # seconds
    AVATAR_OPERATION_TIMEOUT: int = int(os.getenv("AVATAR_OPERATION_TIMEOUT", "30"))
    
    # Avatar Models
    DEFAULT_AVATAR_MODEL: str = os.getenv("DEFAULT_AVATAR_MODEL", "MuseTalk")
    AVAILABLE_AVATAR_MODELS: list = ["MuseTalk", "wav2lip", "ultralight"]
    
    # TTS Models
    DEFAULT_TTS_MODEL: str = os.getenv("DEFAULT_TTS_MODEL", "edge-tts")
    AVAILABLE_TTS_MODELS: list = ["edge-tts", "cosyvoice", "sovits", "tacotron"]
    
    # Avatar Storage (if managing locally)
    AVATAR_STORAGE_PATH: Path = Path(os.getenv(
        "AVATAR_STORAGE_PATH",
        str(Path.home() / "virtual_tutor_avatars")
    ))
    
    # Default settings
    DEFAULT_REF_FILE: str = "ref_audio/silence.wav"
    DEFAULT_REF_TEXT: str = "Hello, I'm your virtual tutor. How can I help you today?"
    
    # WebRTC settings
    WEBRTC_MAX_SESSIONS: int = int(os.getenv("WEBRTC_MAX_SESSIONS", "8"))
    WEBRTC_PORT: int = int(os.getenv("WEBRTC_PORT", "8615"))
    
    @classmethod
    def validate_lipsync_service(cls) -> bool:
        """Validate lip-sync service is available"""
        try:
            import httpx
            response = httpx.get(f"{cls.LIPSYNC_SERVICE_URL}/avatar/get_avatars", timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False
    
    @classmethod
    def validate_tts_service(cls) -> bool:
        """Validate TTS service is available"""
        try:
            import httpx
            response = httpx.get(f"{cls.TTS_SERVICE_URL}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Lip-sync service validation failed: {e}")
            return False
    
    @classmethod
    def validate_tts_service(cls) -> bool:
        """Validate TTS service is available"""
        try:
            import httpx
            response = httpx.get(f"{cls.TTS_SERVICE_URL}/tts/models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"TTS service validation failed: {e}")
            return False
    
    @classmethod
    def ensure_storage_path(cls):
        """Ensure avatar storage directory exists"""
        cls.AVATAR_STORAGE_PATH.mkdir(parents=True, exist_ok=True)


# Global config instance
avatar_config = AvatarConfig()
