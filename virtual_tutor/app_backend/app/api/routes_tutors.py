from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import httpx
import logging
import os

from app.db.session import get_db
from app.models.tutor import Tutor
from app.models.avatar import Avatar
from app.models.admin import Admin
from app.schemas.tutor import TutorCreate, TutorOut
from app.api.deps import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tutors", tags=["tutors"])

# Avatar Service URL
AVATAR_SERVICE_URL = os.getenv("AVATAR_SERVICE_URL", "http://localhost:8001")

# File upload limits
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB


@router.post("/", response_model=TutorOut)
def create_tutor(
    tutor_in: TutorCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    tutor = Tutor(
        admin_id=current_admin.id,
        name=tutor_in.name,
        description=tutor_in.description,
        target_language=tutor_in.target_language,
    )
    db.add(tutor)
    db.commit()
    db.refresh(tutor)
    return tutor


@router.get("/", response_model=List[TutorOut])
def list_tutors(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    tutors = (
        db.query(Tutor)
        .filter(Tutor.admin_id == current_admin.id)  # 多租户隔离关键
        .order_by(Tutor.id.desc())
        .all()
    )
    return tutors


@router.post("/create-with-avatar")
async def create_tutor_with_avatar(
    # Tutor fields
    name: str = Form(..., description="Tutor name"),
    description: Optional[str] = Form(None, description="Tutor description"),
    target_language: str = Form("en", description="Target language"),
    # Avatar fields
    avatar_name: str = Form(..., description="Avatar identifier (must be unique)"),
    avatar_model: str = Form("MuseTalk", description="Avatar model"),
    tts_model: str = Form("edge-tts", description="TTS model"),
    timbre: Optional[str] = Form(None, description="Voice timbre"),
    avatar_blur: bool = Form(False, description="Apply blur effect"),
    support_clone: bool = Form(False, description="Support voice cloning"),
    ref_text: Optional[str] = Form(None, description="Reference text for cloning"),
    # Files
    prompt_face: UploadFile = File(..., description="Video file for avatar"),
    prompt_voice: Optional[UploadFile] = File(None, description="Audio file (optional)"),
    # Dependencies
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new tutor with avatar in one operation (Server A - Web Backend)
    
    This is the unified API for creating tutors with avatars.
    It handles the complete workflow:
    1. Create tutor record in database
    2. Call Avatar Service (Serverless AI Engine) to process avatar
    3. Save avatar metadata to database
    4. Return complete result
    
    This endpoint stays on Server A (not in Docker).
    """
    tutor = None
    try:
        # Validate file sizes
        if prompt_face.size and prompt_face.size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Video file too large. Maximum size: {MAX_VIDEO_SIZE // 1024 // 1024}MB"
            )
        
        if prompt_voice and prompt_voice.size and prompt_voice.size > MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Maximum size: {MAX_AUDIO_SIZE // 1024 // 1024}MB"
            )
        
        # Check avatar name availability BEFORE creating tutor (avoid race condition)
        existing_avatar = db.query(Avatar).filter(Avatar.name == avatar_name).first()
        if existing_avatar:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Avatar with name '{avatar_name}' already exists"
            )
        
        # Step 1: Create Tutor (业务逻辑 - Web Backend 负责)
        logger.info(f"Admin {current_admin.id} creating tutor '{name}' with avatar '{avatar_name}'")
        
        tutor = Tutor(
            admin_id=current_admin.id,
            name=name,
            description=description,
            target_language=target_language,
        )
        db.add(tutor)
        db.commit()
        db.refresh(tutor)
        
        logger.info(f"Tutor {tutor.id} created, proceeding to create avatar...")
        
        # Step 3: Call Avatar Service to process avatar (AI 推理 - Serverless 负责)
        video_bytes = await prompt_face.read()
        audio_bytes = None
        audio_filename = None
        
        if prompt_voice:
            audio_bytes = await prompt_voice.read()
            audio_filename = prompt_voice.filename
        
        # Prepare request to Avatar Service
        files = {
            "prompt_face": (prompt_face.filename, video_bytes, prompt_face.content_type)
        }
        if audio_bytes:
            files["prompt_voice"] = (audio_filename, audio_bytes, "audio/mpeg")
        
        data = {
            "name": avatar_name,
            "avatar_model": avatar_model,
            "tts_model": tts_model,
            "timbre": timbre or "",
            "avatar_blur": str(avatar_blur).lower(),
            "support_clone": str(support_clone).lower(),
            "description": description or ""
        }
        
        logger.info(f"Calling Avatar Service to create avatar '{avatar_name}'...")
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                service_response = await client.post(
                    f"{AVATAR_SERVICE_URL}/api/avatar/create",
                    files=files,
                    data=data
                )
            
            if service_response.status_code != 200:
                # Avatar creation failed, rollback tutor
                logger.error(f"Avatar Service error: {service_response.text}")
                db.delete(tutor)
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Avatar Service error: {service_response.text}"
                )
            
            service_result = service_response.json()
            logger.info(f"Avatar Service response: {service_result}")
            
        except httpx.TimeoutException:
            # Timeout, but avatar might still be processing
            logger.warning(f"Avatar Service timeout, but avatar might still be processing")
            db.delete(tutor)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Avatar creation timeout. This process can take 2-5 minutes. Please try again or check status later."
            )
        except Exception as e:
            logger.error(f"Error calling Avatar Service: {e}")
            db.delete(tutor)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with Avatar Service: {str(e)}"
            )
        
        # Step 4: Save Avatar metadata to database (业务逻辑 - Web Backend 负责)
        try:
            avatar = Avatar(
                tutor_id=tutor.id,
                name=avatar_name,
                display_name=avatar_name,
                avatar_model=avatar_model,
                tts_model=tts_model,
                timbre=timbre,
                avatar_blur=avatar_blur,
                support_clone=support_clone,
                status="active",
                description=description,
                preview_image_path=service_result.get("image_path"),
                video_path=prompt_face.filename,
                audio_path=audio_filename,
                engine_url=AVATAR_SERVICE_URL  # 记录 AI Engine 地址
            )
            
            db.add(avatar)
            db.commit()
            db.refresh(avatar)
        except Exception as db_error:
            # Database save failed - avatar created in service but not recorded
            logger.error(f"Failed to save avatar metadata: {db_error}")
            logger.error(f"⚠️ Avatar '{avatar_name}' created in Avatar Service but not saved to database")
            # Rollback tutor
            db.delete(tutor)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Avatar created but failed to save metadata. Please delete avatar '{avatar_name}' manually from Avatar Service."
            )
        
        logger.info(f"✅ Tutor {tutor.id} with avatar {avatar.id} created successfully")
        
        return {
            "status": "success",
            "message": f"Tutor '{name}' with avatar '{avatar_name}' created successfully",
            "tutor": {
                "id": tutor.id,
                "name": tutor.name,
                "description": tutor.description,
                "target_language": tutor.target_language,
                "created_at": tutor.created_at.isoformat()
            },
            "avatar": {
                "id": avatar.id,
                "name": avatar.name,
                "avatar_model": avatar.avatar_model,
                "tts_model": avatar.tts_model,
                "status": avatar.status,
                "preview_image_path": avatar.preview_image_path
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating tutor with avatar: {e}", exc_info=True)
        # Cleanup: delete tutor if it was created
        if tutor and tutor.id:
            try:
                db.delete(tutor)
                db.commit()
                logger.info(f"Rolled back tutor {tutor.id} due to error")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup tutor: {cleanup_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tutor with avatar: {str(e)}"
        )
