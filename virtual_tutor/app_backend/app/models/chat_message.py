from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChatMessage(Base):
    """
    会话中的一条消息（Q/A 记录）。
    可以按需要选择是否长期保存全文，或者只保存摘要。

    role:
        - student  : 学生说的话（文字或 ASR 转写）
        - assistant: AI 导师的回复（LLM 文本）
        - system   : 系统提示 / 状态信息
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id"),
        nullable=False,
        index=True,
    )

    role = Column(String, nullable=False)  # "student" / "assistant" / "system"
    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # 和Session.messages 对应
    session = relationship("Session", back_populates="messages")
