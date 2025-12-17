from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    # 归属的 Tutor（多租户关键）
    tutor_id = Column(
        Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # 基本信息
    email = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)

    # 登录相关
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tutor = relationship("Tutor", backref="students")
