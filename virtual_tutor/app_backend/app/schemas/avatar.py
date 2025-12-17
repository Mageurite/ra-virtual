from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AvatarBase(BaseModel):
    """Base schema for Avatar"""
    name: str = Field(..., description="Avatar identifier (unique)")
    display_name: Optional[str] = Field(None, description="Human-readable display name")
    description: Optional[str] = Field(None, description="Avatar description")
    avatar_model: str = Field(default="MuseTalk", description="Avatar model type")
    tts_model: str = Field(default="edge-tts", description="TTS model")
    timbre: Optional[str] = Field(None, description="Voice timbre identifier")
    avatar_blur: bool = Field(default=False, description="Apply blur effect")
    support_clone: bool = Field(default=False, description="Support voice cloning")


class AvatarCreate(AvatarBase):
    """Schema for creating a new avatar"""
    tutor_id: int = Field(..., description="Tutor ID this avatar belongs to")


class AvatarUpdate(BaseModel):
    """Schema for updating an avatar (all fields optional)"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    avatar_model: Optional[str] = None
    tts_model: Optional[str] = None
    timbre: Optional[str] = None
    avatar_blur: Optional[bool] = None
    support_clone: Optional[bool] = None
    status: Optional[str] = None
    engine_url: Optional[str] = None


class AvatarInDB(AvatarBase):
    """Schema for avatar as stored in database"""
    id: int
    tutor_id: int
    status: str
    preview_image_path: Optional[str]
    video_path: Optional[str]
    audio_path: Optional[str]
    engine_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AvatarResponse(AvatarInDB):
    """Schema for avatar API responses"""
    pass


class AvatarListResponse(BaseModel):
    """Schema for listing avatars"""
    avatars: list[AvatarResponse]
    total: int


class AvatarStartRequest(BaseModel):
    """Schema for starting an avatar"""
    avatar_id: int = Field(..., description="Avatar ID to start")
    ref_file: Optional[str] = Field(None, description="Reference audio file path")


class AvatarStartResponse(BaseModel):
    """Schema for avatar start response"""
    status: str
    message: str
    engine_url: Optional[str] = None


class AvatarPreviewRequest(BaseModel):
    """Schema for requesting avatar preview"""
    avatar_id: int = Field(..., description="Avatar ID")


class AvatarDeleteRequest(BaseModel):
    """Schema for deleting avatar"""
    avatar_id: int = Field(..., description="Avatar ID to delete")
