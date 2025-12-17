from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Avatar(Base):
    """Avatar model for virtual tutor system
    
    Attributes:
        id: Primary key
        tutor_id: Foreign key to tutor (each avatar belongs to a tutor)
        name: Avatar name/identifier
        display_name: Human-readable display name
        avatar_model: Model type (e.g., 'MuseTalk', 'wav2lip', 'ultralight')
        tts_model: TTS model (e.g., 'edge-tts', 'cosyvoice', 'sovits')
        timbre: Voice timbre/character identifier
        avatar_blur: Whether to apply blur effect
        support_clone: Whether avatar supports voice cloning
        status: Avatar status ('active', 'inactive', 'processing')
        description: Avatar description
        preview_image_path: Path to avatar preview image
        video_path: Path to source video file
        audio_path: Path to reference audio file
        engine_url: Service URL where avatar is running (e.g., 'http://localhost:8615')
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "avatars"

    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant: each avatar belongs to a tutor
    tutor_id = Column(
        Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Basic info
    name = Column(String, nullable=False, unique=True, index=True)
    display_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Model configuration
    avatar_model = Column(String, default="MuseTalk")  # MuseTalk, wav2lip, ultralight
    tts_model = Column(String, default="edge-tts")  # edge-tts, cosyvoice, sovits, tacotron
    timbre = Column(String, nullable=True)  # Voice timbre identifier
    
    # Features
    avatar_blur = Column(Boolean, default=False)
    support_clone = Column(Boolean, default=False)
    
    # Status
    status = Column(String, default="inactive")  # active, inactive, processing, error
    
    # File paths
    preview_image_path = Column(String, nullable=True)  # Preview image
    video_path = Column(String, nullable=True)  # Source video
    audio_path = Column(String, nullable=True)  # Reference audio
    
    # Engine info
    engine_url = Column(String, nullable=True)  # Service URL (e.g., http://localhost:8615)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    tutor = relationship("Tutor", backref="avatars")
