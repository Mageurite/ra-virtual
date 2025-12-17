"""
TTS API Routes - Serverless AI Engine
Provides text-to-speech synthesis endpoints
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from tts.service import get_tts_service
from tts.config import tts_config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class TTSRequest(BaseModel):
    """TTS synthesis request"""
    text: str = Field(..., description="Text to synthesize", max_length=5000)
    engine: Optional[str] = Field(None, description="TTS engine (edge-tts, cosyvoice, gpt-sovits)")
    voice: Optional[str] = Field(None, description="Voice ID")
    rate: float = Field(1.0, description="Speech rate (0.5 - 2.0)", ge=0.5, le=2.0)
    volume: float = Field(1.0, description="Volume (0.0 - 1.0)", ge=0.0, le=1.0)


class VoiceInfo(BaseModel):
    """Voice information"""
    id: str
    name: str
    lang: str
    engine: Optional[str] = None


class EngineInfo(BaseModel):
    """TTS engine information"""
    id: str
    name: str
    description: str
    requires_reference: bool


class TTSHealthResponse(BaseModel):
    """TTS health check response"""
    status: str
    service_url: str
    engines: List[str]


# ============================================================================
# TTS Endpoints
# ============================================================================

@router.post("/synthesize")
async def synthesize_speech(
    text: str = Form(..., description="Text to synthesize"),
    engine: Optional[str] = Form(None, description="TTS engine"),
    voice: Optional[str] = Form(None, description="Voice ID"),
    rate: float = Form(1.0, description="Speech rate"),
    volume: float = Form(1.0, description="Volume"),
    reference_audio: Optional[UploadFile] = File(None, description="Reference audio for voice cloning")
):
    """
    Synthesize speech from text
    
    Returns WAV audio file
    """
    try:
        tts_service = get_tts_service()
        
        # Read reference audio if provided
        ref_audio_bytes = None
        if reference_audio:
            ref_audio_bytes = await reference_audio.read()
        
        # Synthesize
        audio_data = await tts_service.synthesize(
            text=text,
            engine=engine,
            voice=voice,
            rate=rate,
            volume=volume,
            reference_audio=ref_audio_bytes
        )
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="speech.wav"'
            }
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.post("/synthesize-json")
async def synthesize_speech_json(request: TTSRequest):
    """
    Synthesize speech from text (JSON input)
    
    Returns WAV audio file
    """
    try:
        tts_service = get_tts_service()
        
        audio_data = await tts_service.synthesize(
            text=request.text,
            engine=request.engine,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume
        )
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="speech.wav"'
            }
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.post("/clone")
async def clone_voice(
    text: str = Form(..., description="Text to synthesize"),
    voice_name: Optional[str] = Form(None, description="Voice name"),
    reference_audio: UploadFile = File(..., description="Reference audio file")
):
    """
    Clone voice from reference audio and synthesize text
    
    Returns WAV audio file with cloned voice
    """
    try:
        tts_service = get_tts_service()
        
        # Read reference audio
        ref_audio_bytes = await reference_audio.read()
        
        # Clone and synthesize
        audio_data = await tts_service.clone_voice(
            reference_audio=ref_audio_bytes,
            text=text,
            voice_name=voice_name
        )
        
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f'attachment; filename="cloned_speech.wav"'
            }
        )
        
    except Exception as e:
        logger.error(f"Voice cloning error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice cloning failed: {str(e)}"
        )


# ============================================================================
# Query Endpoints
# ============================================================================

@router.get("/voices", response_model=List[VoiceInfo])
async def get_voices(engine: Optional[str] = None):
    """
    Get available voices
    
    Args:
        engine: Filter by TTS engine (optional)
    
    Returns:
        List of available voices
    """
    try:
        tts_service = get_tts_service()
        voices = await tts_service.get_available_voices(engine)
        return voices
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        # Fallback to config
        if engine:
            return tts_config.get_voices_for_engine(engine)
        
        all_voices = []
        for eng in tts_config.AVAILABLE_ENGINES:
            voices = tts_config.get_voices_for_engine(eng)
            for voice in voices:
                voice["engine"] = eng
            all_voices.extend(voices)
        return all_voices


@router.get("/engines", response_model=List[EngineInfo])
async def get_engines():
    """
    Get available TTS engines
    
    Returns:
        List of TTS engines with capabilities
    """
    try:
        tts_service = get_tts_service()
        engines = await tts_service.get_available_engines()
        return engines
        
    except Exception as e:
        logger.error(f"Error getting engines: {e}")
        return [
            {
                "id": "edge-tts",
                "name": "Microsoft Edge TTS",
                "description": "Free online TTS service",
                "requires_reference": False,
            },
            {
                "id": "cosyvoice",
                "name": "CosyVoice",
                "description": "High-quality local TTS",
                "requires_reference": False,
            },
            {
                "id": "gpt-sovits",
                "name": "GPT-SoVITS",
                "description": "Voice cloning TTS",
                "requires_reference": True,
            },
        ]


@router.get("/health", response_model=TTSHealthResponse)
async def health_check():
    """
    Check TTS service health
    """
    try:
        tts_service = get_tts_service()
        health = await tts_service.health_check()
        
        if health["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TTS service is unavailable"
            )
        
        return health
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )
