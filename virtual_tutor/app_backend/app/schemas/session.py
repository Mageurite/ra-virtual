from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.chat_message import ChatMessageOut


class SessionBase(BaseModel):
    id: int
    tutor_id: int
    student_id: int
    status: str
    engine_url: Optional[str] = None
    engine_token: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True  # 兼容 SQLAlchemy ORM 对象
        

class SessionCreate(BaseModel):
    """
    目前先不让学生传任何字段：
    - tutor_id 从 current_student.tutor_id 拿
    - student_id 从 current_student.id 拿
    后面如果要加 topic / metadata 再扩展这个模型。
    """
    pass

class SessionOut(SessionBase):
    """
    返回给前端用的 Session 模型。
    先直接继承 SessionBase 即可，如果以后需要隐藏 engine_token，
    可以再单独定义一个对外展示模型。
    """
    pass

class SessionWithMessages(SessionOut):
    """
    带消息列表的 Session 详情，用于：
    - GET /api/student/sessions/{session_id}
    这种需要返回整个会话历史的接口。
    """
    messages: List[ChatMessageOut] = []

    class Config:
        orm_mode = True  # 再写一遍也没问题，清晰一点
