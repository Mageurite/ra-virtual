"""
Avatar API routes - Serverless AI Engine
Pure avatar management without database dependencies
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from avatar.service import get_avatar_service
from avatar.config import avatar_config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class AvatarListResponse(BaseModel):
    """Avatar list response"""
    avatars: List[str]
    total: int


class AvatarCreateResponse(BaseModel):
    """Avatar creation response"""
    status: str
    message: str
    avatar_name: str
    image_path: Optional[str] = None


class AvatarStartResponse(BaseModel):
    """Avatar start response"""
    status: str
    message: str
    engine_url: Optional[str] = None


# ============================================================================
# WebRTC Proxy
# ============================================================================

@router.api_route(
    "/webrtc/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    include_in_schema=False
)
async def webrtc_proxy(path: str, request: Request):
    """Proxy WebRTC requests to lip-sync service"""
    try:
        import httpx
        
        webrtc_url = f"{avatar_config.LIPSYNC_SERVICE_URL}/{path}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get request body for POST/PUT methods
            body = None
            if request.method in ["POST", "PUT"]:
                body = await request.body()
            
            response = await client.request(
                method=request.method,
                url=webrtc_url,
                content=body,
                headers={
                    key: value for key, value in request.headers.items()
                    if key.lower() not in ["host", "content-length"]
                }
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except Exception as e:
        logger.error(f"WebRTC proxy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"WebRTC proxy error: {str(e)}"
        )


# ============================================================================
# Avatar Operations
# ============================================================================

@router.get("/list", response_model=AvatarListResponse)
async def list_avatars():
    """List all available avatars"""
    try:
        avatar_service = get_avatar_service()
        avatars = await avatar_service.list_avatars()
        
        return AvatarListResponse(
            avatars=avatars,
            total=len(avatars)
        )
    except Exception as e:
        logger.error(f"Error listing avatars: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list avatars: {str(e)}"
        )


@router.post("/create", response_model=AvatarCreateResponse)
async def create_avatar(
    name: str = Form(..., description="Avatar identifier"),
    avatar_model: str = Form("MuseTalk", description="Avatar model"),
    tts_model: str = Form("edge-tts", description="TTS model"),
    timbre: Optional[str] = Form(None, description="Voice timbre"),
    avatar_blur: bool = Form(False, description="Apply blur effect"),
    support_clone: bool = Form(False, description="Support voice cloning"),
    description: Optional[str] = Form(None, description="Avatar description"),
    prompt_face: UploadFile = File(..., description="Video file"),
    prompt_voice: Optional[UploadFile] = File(None, description="Audio file (optional)"),
):
    """
    Create a new avatar
    
    Upload a video file to create an avatar.
    Optionally include audio file for voice cloning.
    """
    try:
        avatar_service = get_avatar_service()
        
        # Read files
        video_bytes = await prompt_face.read()
        audio_bytes = None
        audio_filename = None
        
        if prompt_voice:
            audio_bytes = await prompt_voice.read()
            audio_filename = prompt_voice.filename
        
        # Create avatar
        result = await avatar_service.create_avatar(
            name=name,
            video_file=video_bytes,
            video_filename=prompt_face.filename,
            avatar_blur=avatar_blur,
            support_clone=support_clone,
            timbre=timbre,
            tts_model=tts_model,
            avatar_model=avatar_model,
            description=description,
            audio_file=audio_bytes,
            audio_filename=audio_filename
        )
        
        return AvatarCreateResponse(
            status="success",
            message=f"Avatar '{name}' created successfully",
            avatar_name=name,
            image_path=result.get("image_path")
        )
        
    except Exception as e:
        logger.error(f"Error creating avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar creation failed: {str(e)}"
        )


@router.post("/start", response_model=AvatarStartResponse)
async def start_avatar(
    avatar_name: str = Form(..., description="Avatar name"),
    ref_file: Optional[str] = Form(None, description="Reference audio file path")
):
    """
    Start an avatar (launch WebRTC service)
    
    This can take 1-5 minutes as it loads the model.
    """
    try:
        avatar_service = get_avatar_service()
        
        result = await avatar_service.start_avatar(
            avatar_name=avatar_name,
            ref_file=ref_file
        )
        
        return AvatarStartResponse(
            status="success",
            message=f"Avatar '{avatar_name}' started successfully",
            engine_url=avatar_config.LIPSYNC_SERVICE_URL
        )
        
    except Exception as e:
        logger.error(f"Error starting avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar start failed: {str(e)}"
        )


@router.get("/preview/{avatar_name}")
async def get_avatar_preview(avatar_name: str):
    """Get avatar preview image (returns PNG)"""
    try:
        avatar_service = get_avatar_service()
        image_bytes = await avatar_service.get_avatar_preview(avatar_name)
        
        return Response(
            content=image_bytes,
            media_type="image/png"
        )
        
    except Exception as e:
        logger.error(f"Error getting avatar preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preview: {str(e)}"
        )


@router.delete("/delete")
async def delete_avatar(avatar_name: str = Form(..., description="Avatar name")):
    """Delete an avatar"""
    try:
        avatar_service = get_avatar_service()
        result = await avatar_service.delete_avatar(avatar_name)
        
        return {
            "status": "success",
            "message": f"Avatar '{avatar_name}' deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete avatar: {str(e)}"
        )


# ============================================================================
# Utility Endpoints
# ============================================================================

@router.get("/tts-models")
async def get_tts_models():
    """Get list of available TTS models"""
    try:
        avatar_service = get_avatar_service()
        models = await avatar_service.get_tts_models()
        return {"models": models}
    except Exception as e:
        logger.warning(f"Error getting TTS models: {e}")
        return {
            "models": [
                {"id": "edge-tts", "name": "Edge TTS"},
                {"id": "cosyvoice", "name": "CosyVoice"},
                {"id": "sovits", "name": "GPT-SoVITS"},
                {"id": "tacotron", "name": "Tacotron2"}
            ]
        }


@router.get("/avatar-models")
async def get_avatar_models():
    """Get list of supported avatar models"""
    return {
        "models": [
            {"id": "MuseTalk", "name": "MuseTalk", "description": "High-quality lip-sync model"},
            {"id": "wav2lip", "name": "Wav2Lip", "description": "Fast lip-sync model"},
            {"id": "ultralight", "name": "UltraLight", "description": "Lightweight model"}
        ]
    }


@router.get("/health")
async def avatar_health_check():
    """Check health of avatar services"""
    try:
        avatar_service = get_avatar_service()
        health = await avatar_service.health_check()
        
        if not health["all_healthy"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="One or more avatar services are unavailable"
            )
        
        return health
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )
