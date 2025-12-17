from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TutorBase(BaseModel):
    name: str
    description: str | None = None
    target_language: str | None = None


class TutorCreate(TutorBase):
    """用于创建 Tutor 的入参"""
    pass


class TutorOut(TutorBase):
    """返回给前端的 Tutor 数据"""
    id: int
    created_at: datetime

    # pydantic v2 用法：从 ORM 对象读取字段
    model_config = ConfigDict(from_attributes=True)
