"""
Public Avatar Access Routes - Proxy to Avatar Service
学生公开访问路由 - 代理模式（无需认证）
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import httpx
import os

from app.db.session import get_db
from app.models.tutor import Tutor
from app.models.avatar import Avatar

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tutors", tags=["public-tutors"])

# Avatar Service URL (Serverless AI Engine)
AVATAR_SERVICE_URL = os.getenv("AVATAR_SERVICE_URL", "http://localhost:8001")


# ============================================================================
# Response Models
# ============================================================================

class TutorInfoResponse(BaseModel):
    """Tutor information for public access"""
    id: int
    name: str
    description: Optional[str]
    target_language: Optional[str]
    has_avatar: bool
    avatar_status: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Public Tutor Endpoints (No Authentication Required)
# ============================================================================

@router.get("/{tutor_id}/info", response_model=TutorInfoResponse)
async def get_tutor_info(
    tutor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public tutor information (No authentication)
    学生通过分享的 URL 访问 Tutor 信息
    """
    try:
        tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
        
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # 检查是否有 Avatar
        avatar = db.query(Avatar).filter(Avatar.tutor_id == tutor_id).first()
        
        return TutorInfoResponse(
            id=tutor.id,
            name=tutor.name,
            description=tutor.description,
            target_language=tutor.target_language,
            has_avatar=avatar is not None,
            avatar_status=avatar.status if avatar else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tutor info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tutor info: {str(e)}"
        )


@router.post("/{tutor_id}/chat")
async def chat_with_tutor(
    tutor_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Chat with tutor's LLM (proxy to Avatar Service)
    学生与 Tutor 的 LLM 对话（无需认证）
    """
    try:
        # 1. 验证 Tutor 存在 (Web Back-End)
        tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
        
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # 2. 转发到 Avatar Service (AI Engine)
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/api/chat/completion",
                content=body,
                headers={"Content-Type": "application/json"}
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Avatar Service error: {response.text}"
            )
        
        return response.json()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/{tutor_id}/chat/stream")
async def chat_with_tutor_stream(
    tutor_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Chat with tutor's LLM - streaming (proxy to Avatar Service)
    学生与 Tutor 的 LLM 对话 - 流式（无需认证）
    """
    try:
        # 1. 验证 Tutor 存在 (Web Back-End)
        tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
        
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        # 2. 转发到 Avatar Service 并流式返回 (AI Engine)
        body = await request.body()
        
        async def stream_proxy():
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{AVATAR_SERVICE_URL}/api/chat/stream",
                    content=body,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        return StreamingResponse(
            stream_proxy(),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat stream failed: {str(e)}"
        )


@router.get("/{tutor_id}/avatar/preview")
async def get_avatar_preview(
    tutor_id: int,
    db: Session = Depends(get_db)
):
    """
    Get avatar preview image (proxy to Avatar Service)
    获取 Avatar 预览图（无需认证）
    """
    try:
        # 1. 查询 Avatar (Web Back-End)
        avatar = db.query(Avatar).filter(Avatar.tutor_id == tutor_id).first()
        
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This tutor does not have an avatar"
            )
        
        # 2. 转发到 Avatar Service (AI Engine)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AVATAR_SERVICE_URL}/api/avatar/preview/{avatar.name}"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to get avatar preview"
            )
        
        return Response(
            content=response.content,
            media_type="image/png"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting avatar preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get avatar preview: {str(e)}"
        )


@router.api_route(
    "/{tutor_id}/webrtc/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    include_in_schema=False
)
async def webrtc_proxy(
    tutor_id: int,
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Proxy WebRTC requests to Avatar Service
    代理 WebRTC 请求到 Avatar Service（无需认证）
    """
    try:
        # 1. 验证 Avatar 存在并运行 (Web Back-End)
        avatar = db.query(Avatar).filter(Avatar.tutor_id == tutor_id).first()
        
        if not avatar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar not found for this tutor"
            )
        
        if avatar.status != "running":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Avatar is not running. Please ask admin to start it."
            )
        
        # 2. 转发到 Avatar Service (AI Engine)
        webrtc_url = f"{AVATAR_SERVICE_URL}/api/avatar/webrtc/{path}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            body = await request.body() if request.method in ["POST", "PUT"] else None
            
            response = await client.request(
                method=request.method,
                url=webrtc_url,
                content=body,
                headers=dict(request.headers)
            )
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WebRTC proxy error: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"WebRTC proxy error: {str(e)}"
        )


@router.get("/{tutor_id}/health")
async def tutor_health_check(
    tutor_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if tutor and its avatar are available
    检查 Tutor 服务是否可用（无需认证）
    """
    try:
        tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
        
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor not found"
            )
        
        avatar = db.query(Avatar).filter(Avatar.tutor_id == tutor_id).first()
        
        # 检查 Avatar Service 健康状态
        avatar_service_healthy = False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{AVATAR_SERVICE_URL}/health")
                avatar_service_healthy = response.status_code == 200
        except:
            pass
        
        return {
            "status": "ok",
            "tutor_id": tutor_id,
            "tutor_name": tutor.name,
            "has_avatar": avatar is not None,
            "avatar_status": avatar.status if avatar else None,
            "avatar_running": avatar.status == "running" if avatar else False,
            "avatar_service_healthy": avatar_service_healthy
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
