from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Session(Base):
    """
    一次“上课会话”的元数据，用于日志 & 审计 & 后续历史查询。

    核心字段：
    - tutor_id / student_id：多租户隔离（Tutor 是租户边界）
    - engine_url / engine_token：前端接入 AI 引擎所需信息
    - started_at / ended_at：会话起止时间
    - status：方便区分进行中 / 已结束
    """

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    # 多租户关键字段：这条 Session 属于哪个 Tutor / 学生
    tutor_id = Column(Integer, ForeignKey("tutors.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    # 可选：冗余存一下 admin_id，方便按管理员过滤 Session
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True, index=True)

    # AI 引擎那边的会话标识（如果有的话）
    engine_session_id = Column(String, nullable=True)

    # 给前端的“门票”信息（由应用后端从 AI 引擎的管理 API 拿到）
    engine_url = Column(String, nullable=True)
    engine_token = Column(String, nullable=True)

    # pending / active / ended 等，你后面可以用 Enum 替换
    status = Column(String, nullable=False, default="pending")

    started_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
