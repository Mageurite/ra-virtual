from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Tutor(Base):
    __tablename__ = "tutors"

    id = Column(Integer, primary_key=True, index=True)

    # 多租户关键：每个 Tutor 归属于一个 Admin
    admin_id = Column(
        Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_language = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 关系（可选，用于以后方便查询）
    admin = relationship("Admin", backref="tutors")
