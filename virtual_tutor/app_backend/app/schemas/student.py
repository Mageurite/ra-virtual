from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class StudentBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True


class StudentCreate(StudentBase):
    # Admin 创建学生时设置初始密码
    password: str


class StudentUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    password: str | None = None  # Admin 可以重置密码


class StudentOut(StudentBase):
    id: int
    tutor_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentLogin(BaseModel):
    email: EmailStr
    password: str
    tutor_id: int  # 防止不同 Tutor 下同邮箱冲突
