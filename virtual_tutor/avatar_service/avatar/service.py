"""
Avatar Service Client
Handles communication with lip-sync and TTS services
"""
import httpx
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from avatar.config import avatar_config

logger = logging.getLogger(__name__)


class AvatarServiceClient:
    """Client for Avatar/Lip-Sync service operations"""
    
    def __init__(self):
        self.base_url = avatar_config.LIPSYNC_SERVICE_URL
        self.tts_url = avatar_config.TTS_SERVICE_URL
    
    async def list_avatars(self) -> List[str]:
        """
        Get list of available avatars from lip-sync service
        
        Returns:
            List of avatar names
        """
        try:
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_OPERATION_TIMEOUT) as client:
                response = await client.get(f"{self.base_url}/avatar/get_avatars")
                response.raise_for_status()
                
                data = response.json()
                if data.get("status") == "success":
                    return data.get("avatars", [])
                return []
                
        except Exception as e:
            logger.error(f"Error listing avatars: {e}")
            return []
    
    async def create_avatar(
        self,
        name: str,
        video_file: bytes,
        video_filename: str,
        avatar_blur: bool = False,
        support_clone: bool = False,
        timbre: Optional[str] = None,
        tts_model: Optional[str] = None,
        avatar_model: Optional[str] = None,
        description: Optional[str] = None,
        audio_file: Optional[bytes] = None,
        audio_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new avatar
        
        Args:
            name: Avatar identifier
            video_file: Video file bytes
            video_filename: Original video filename
            avatar_blur: Apply blur effect
            support_clone: Support voice cloning
            timbre: Voice timbre
            tts_model: TTS model to use
            avatar_model: Avatar model to use
            description: Avatar description
            audio_file: Optional audio file bytes
            audio_filename: Optional audio filename
        
        Returns:
            Creation result dict
        """
        try:
            # Prepare files
            files = {
                "prompt_face": (video_filename, video_file, "video/mp4")
            }
            
            if audio_file and audio_filename:
                files["prompt_voice"] = (audio_filename, audio_file, "audio/wav")
            
            # Prepare form data
            data = {
                "name": name,
                "avatar_blur": str(avatar_blur).lower(),
                "support_clone": str(support_clone).lower(),
                "timbre": timbre or "",
                "tts_model": tts_model or avatar_config.DEFAULT_TTS_MODEL,
                "avatar_model": avatar_model or avatar_config.DEFAULT_AVATAR_MODEL,
                "description": description or "",
            }
            
            # Send request
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_CREATE_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/avatar/add",
                    data=data,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Avatar '{name}' created: {result}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error creating avatar: {e}")
            raise Exception(f"Avatar creation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating avatar: {e}")
            raise
    
    async def start_avatar(
        self,
        avatar_name: str,
        ref_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an avatar (launch WebRTC service)
        
        Args:
            avatar_name: Name of avatar to start
            ref_file: Reference audio file path (optional)
        
        Returns:
            Start result dict
        """
        try:
            data = {
                "avatar_name": avatar_name,
                "ref_file": ref_file or avatar_config.DEFAULT_REF_FILE
            }
            
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_START_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/avatar/start",
                    data=data
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Avatar '{avatar_name}' started: {result}")
                return result
                
        except httpx.TimeoutException:
            logger.error(f"Timeout starting avatar '{avatar_name}'")
            raise Exception("Avatar start timeout - this can take 1-5 minutes")
        except Exception as e:
            logger.error(f"Error starting avatar: {e}")
            raise
    
    async def get_avatar_preview(self, avatar_name: str) -> bytes:
        """
        Get avatar preview image
        
        Args:
            avatar_name: Name of avatar
        
        Returns:
            Image bytes
        """
        try:
            data = {"avatar_name": avatar_name}
            
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_OPERATION_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/avatar/preview",
                    data=data
                )
                response.raise_for_status()
                
                return response.content
                
        except Exception as e:
            logger.error(f"Error getting avatar preview: {e}")
            raise
    
    async def delete_avatar(self, avatar_name: str) -> Dict[str, Any]:
        """
        Delete an avatar
        
        Args:
            avatar_name: Name of avatar to delete
        
        Returns:
            Deletion result dict
        """
        try:
            data = {"name": avatar_name}
            
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_OPERATION_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/avatar/delete",
                    data=data
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Avatar '{avatar_name}' deleted: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Error deleting avatar: {e}")
            raise
    
    async def get_tts_models(self) -> List[Dict[str, str]]:
        """
        Get available TTS models
        
        Returns:
            List of TTS model info
        """
        try:
            async with httpx.AsyncClient(timeout=avatar_config.AVATAR_OPERATION_TIMEOUT) as client:
                response = await client.get(f"{self.tts_url}/tts/models")
                response.raise_for_status()
                
                data = response.json()
                return data.get("models", [])
                
        except Exception as e:
            logger.warning(f"Error getting TTS models: {e}, using defaults")
            # Return default models
            return [
                {"id": "edge-tts", "name": "Edge TTS"},
                {"id": "cosyvoice", "name": "CosyVoice"},
                {"id": "sovits", "name": "GPT-SoVITS"},
                {"id": "tacotron", "name": "Tacotron2"}
            ]
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of avatar services
        
        Returns:
            Dict with service health status
        """
        lipsync_ok = avatar_config.validate_lipsync_service()
        tts_ok = avatar_config.validate_tts_service()
        
        return {
            "lipsync_service": lipsync_ok,
            "tts_service": tts_ok,
            "all_healthy": lipsync_ok and tts_ok
        }


# Singleton instance
_avatar_service_instance = None


def get_avatar_service() -> AvatarServiceClient:
    """Get or create avatar service instance"""
    global _avatar_service_instance
    if _avatar_service_instance is None:
        _avatar_service_instance = AvatarServiceClient()
    return _avatar_service_instance
