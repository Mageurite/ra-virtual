"""
Avatar Service Module
Provides avatar management and lip-sync integration
"""
from .config import AvatarConfig, avatar_config
from .service import AvatarServiceClient, get_avatar_service

__all__ = [
    'AvatarConfig',
    'avatar_config',
    'AvatarServiceClient',
    'get_avatar_service',
]
