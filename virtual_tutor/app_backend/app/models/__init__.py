# 这里导入所有模型，确保 Base.metadata.create_all() 能看到
from app.db.session import Base  # noqa: F401

from .admin import Admin  # noqa: F401
from .tutor import Tutor  # noqa: F401
from .student import Student # noqa: F401
from .avatar import Avatar  # noqa: F401

from .session import Session
from .chat_message import ChatMessage