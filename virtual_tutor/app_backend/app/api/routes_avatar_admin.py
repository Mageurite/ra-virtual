"""
Admin Avatar Management Routes - Proxy to Avatar Service
管理员专用的 Avatar 管理 API - 代理模式
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import httpx
import os

from app.db.session import get_db
from app.models.admin import Admin
from app.models.tutor import Tutor
from app.models.avatar import Avatar
from app.api.deps import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/avatars", tags=["admin-avatars"])

# Avatar Service URL (Serverless AI Engine)
AVATAR_SERVICE_URL = os.getenv("AVATAR_SERVICE_URL", "http://localhost:8001")


# ============================================================================
# Response Models
# ============================================================================

class AvatarCreateResponse(BaseModel):
    """Avatar creation response"""
    status: str
    message: str
    avatar_id: int
    avatar_name: str
    tutor_id: int
    image_path: Optional[str] = None


class AvatarInfoResponse(BaseModel):
    """Avatar information response"""
    id: int
    tutor_id: int
    tutor_name: str
    name: str
    display_name: Optional[str]
    avatar_model: str
    tts_model: str
    timbre: Optional[str]
    status: str
    description: Optional[str]
    preview_image_path: Optional[str]
    engine_url: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class AvatarListResponse(BaseModel):
    """Avatar list response"""
    avatars: List[AvatarInfoResponse]
    total: int


# ============================================================================
# Avatar Management Endpoints (Admin Only)
# ============================================================================

@router.post("/create", response_model=AvatarCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar_for_tutor(
    tutor_id: int = Form(..., description="Tutor ID to assign avatar to"),
    name: str = Form(..., description="Avatar identifier (must be unique)"),
    display_name: Optional[str] = Form(None, description="Human-readable display name"),
    avatar_model: str = Form("MuseTalk", description="Avatar model"),
    tts_model: str = Form("edge-tts", description="TTS model"),
    timbre: Optional[str] = Form(None, description="Voice timbre"),
    avatar_blur: bool = Form(False, description="Apply blur effect"),
    support_clone: bool = Form(False, description="Support voice cloning"),
    description: Optional[str] = Form(None, description="Avatar description"),
    prompt_face: UploadFile = File(..., description="Video file for avatar"),
    prompt_voice: Optional[UploadFile] = File(None, description="Audio file (optional)"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new avatar for a tutor (Admin only)
    
    Workflow:
    1. Verify the tutor belongs to current admin (Web Back-End 负责)
    2. Proxy request to Avatar Service (Serverless AI Engine)
    3. Save avatar metadata to database (Web Back-End 负责)
    4. Return avatar information
    """
    try:
        # 1. 验证 Tutor 属于当前 Admin (业务逻辑 - Web Back-End 负责)
        tutor = db.query(Tutor).filter(
            Tutor.id == tutor_id,
            Tutor.admin_id == current_admin.id
        ).first()
        
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tutor {tutor_id} not found or you don't have permission"
            )
        
        # 2. 检查 Avatar 名称是否已存在
        existing_avatar = db.query(Avatar).filter(Avatar.name == name).first()
        if existing_avatar:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Avatar with name '{name}' already exists"
            )
        
        # 3. 转发请求到 Avatar Service (AI 推理 - Serverless 负责)
        video_bytes = await prompt_face.read()
        audio_bytes = None
        audio_filename = None
        
        if prompt_voice:
            audio_bytes = await prompt_voice.read()
            audio_filename = prompt_voice.filename
        
        # 准备请求数据
        files = {
            "prompt_face": (prompt_face.filename, video_bytes, prompt_face.content_type)
        }
        if audio_bytes:
            files["prompt_voice"] = (audio_filename, audio_bytes, "audio/mpeg")
        
        data = {
            "name": name,
            "avatar_model": avatar_model,
            "tts_model": tts_model,
            "timbre": timbre or "",
            "avatar_blur": str(avatar_blur).lower(),
            "support_clone": str(support_clone).lower(),
            "description": description or ""
        }
        
        # 调用 Avatar Service
        async with httpx.AsyncClient(timeout=300.0) as client:
            service_response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/avatar/create",
                files=files,
                data=data
            )
        
        if service_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Avatar Service error: {service_response.text}"
            )
        
        service_result = service_response.json()
        
        # 4. 保存 Avatar 元数据到数据库 (业务逻辑 - Web Back-End 负责)
        avatar = Avatar(
            tutor_id=tutor_id,
            name=name,
            display_name=display_name or name,
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
        
        logger.info(f"Admin {current_admin.id} created avatar {avatar.id} for tutor {tutor_id}")
        
        return AvatarCreateResponse(
            status="success",
            message=f"Avatar '{name}' created successfully for tutor '{tutor.name}'",
            avatar_id=avatar.id,
            avatar_name=name,
            tutor_id=tutor_id,
            image_path=avatar.preview_image_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating avatar: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar creation failed: {str(e)}"
        )


@router.get("/list", response_model=AvatarListResponse)
async def list_admin_avatars(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    List all avatars belonging to current admin's tutors
    (Pure database query - no need to call Avatar Service)
    """
    try:
        # 查询当前 Admin 所有 Tutors 的 Avatars (数据库操作 - Web Back-End)
        avatars = (
            db.query(Avatar, Tutor.name.label("tutor_name"))
            .join(Tutor, Avatar.tutor_id == Tutor.id)
            .filter(Tutor.admin_id == current_admin.id)
            .order_by(Avatar.created_at.desc())
            .all()
        )
        
        avatar_list = []
        for avatar, tutor_name in avatars:
            avatar_list.append(
                AvatarInfoResponse(
                    id=avatar.id,
                    tutor_id=avatar.tutor_id,
                    tutor_name=tutor_name,
                    name=avatar.name,
                    display_name=avatar.display_name,
                    avatar_model=avatar.avatar_model,
                    tts_model=avatar.tts_model,
                    timbre=avatar.timbre,
                    status=avatar.status,
                    description=avatar.description,
                    preview_image_path=avatar.preview_image_path,
                    engine_url=avatar.engine_url,
                    created_at=avatar.created_at.isoformat() if avatar.created_at else None
                )
            )
        
        return AvatarListResponse(
            avatars=avatar_list,
            total=len(avatar_list)
        )
        
    except Exception as e:
        logger.error(f"Error listing avatars: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list avatars: {str(e)}"
        )


@router.post("/{avatar_id}/start")
async def start_avatar(
    avatar_id: int,
    ref_file: Optional[str] = Form(None, description="Reference audio file path"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Start an avatar (proxy to Avatar Service)
    """
    try:
        # 1. 验证权限 (Web Back-End)
        avatar = (
            db.query(Avatar)
            .join(Tutor, Avatar.tutor_id == Tutor.id)
            .filter(
                Avatar.id == avatar_id,
                Tutor.admin_id == current_admin.id
            )
            .first()
        )
        
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar not found or access denied"
            )
        
        # 2. 转发到 Avatar Service (AI Engine)
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/avatar/start",
                data={
                    "avatar_name": avatar.name,
                    "ref_file": ref_file or ""
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Avatar Service error: {response.text}"
            )
        
        # 3. 更新数据库状态 (Web Back-End)
        avatar.status = "running"
        db.commit()
        
        return {
            "status": "success",
            "message": f"Avatar '{avatar.name}' started successfully",
            "engine_url": avatar.engine_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting avatar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Avatar start failed: {str(e)}"
        )


@router.delete("/{avatar_id}")
async def delete_avatar(
    avatar_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete an avatar (proxy to Avatar Service + database cleanup)
    """
    try:
        # 1. 验证权限 (Web Back-End)
        avatar = (
            db.query(Avatar)
            .join(Tutor, Avatar.tutor_id == Tutor.id)
            .filter(
                Avatar.id == avatar_id,
                Tutor.admin_id == current_admin.id
            )
            .first()
        )
        
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar not found or access denied"
            )
        
        # 2. 从 Avatar Service 删除 (AI Engine)
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method="DELETE",
                url=f"{AVATAR_SERVICE_URL}/api/avatar/delete",
                data={"avatar_name": avatar.name}
            )
        
        # 即使 Avatar Service 失败，也继续删除数据库记录
        if response.status_code != 200:
            logger.warning(f"Avatar Service delete failed: {response.text}")
        
        # 3. 从数据库删除元数据 (Web Back-End)
        avatar_name = avatar.name
        db.delete(avatar)
        db.commit()
        
        logger.info(f"Admin {current_admin.id} deleted avatar {avatar_id}")
        
        return {
            "status": "success",
            "message": f"Avatar '{avatar_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting avatar: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete avatar: {str(e)}"
        )


@router.get("/{avatar_id}/info", response_model=AvatarInfoResponse)
async def get_avatar_info(
    avatar_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get detailed information about a specific avatar
    (Pure database query - no need to call Avatar Service)
    """
    try:
        # 验证权限并获取 Avatar 和 Tutor 信息 (Web Back-End)
        result = (
            db.query(Avatar, Tutor.name.label("tutor_name"))
            .join(Tutor, Avatar.tutor_id == Tutor.id)
            .filter(
                Avatar.id == avatar_id,
                Tutor.admin_id == current_admin.id
            )
            .first()
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar not found or access denied"
            )
        
        avatar, tutor_name = result
        
        return AvatarInfoResponse(
            id=avatar.id,
            tutor_id=avatar.tutor_id,
            tutor_name=tutor_name,
            name=avatar.name,
            display_name=avatar.display_name,
            avatar_model=avatar.avatar_model,
            tts_model=avatar.tts_model,
            timbre=avatar.timbre,
            status=avatar.status,
            description=avatar.description,
            preview_image_path=avatar.preview_image_path,
            engine_url=avatar.engine_url,
            created_at=avatar.created_at.isoformat() if avatar.created_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting avatar info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatar info: {str(e)}"
        )
