# app/schemas/chat_message.py
from datetime import datetime
from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    role: str        # "student" / "assistant" / "system"
    content: str


class ChatMessageCreate(ChatMessageBase):
    """
    学生/助手发送消息时用的输入模型。
    目前只需要 role + content。
    """
    pass


class ChatMessageOut(ChatMessageBase):
    """
    返回给前端看的消息模型。
    """
    id: int
    session_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: from_orm -> from_attributes
