from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.student import Student
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/api/student/auth", tags=["student-auth"])


@router.post("/login", response_model=Token)
def login_student(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    学生登录（OAuth2 Password Flow）

    - username: 学生邮箱，例如 student1@example.com
    - password: 学生密码
    """
    email = form_data.username
    plain_password = form_data.password

     # 只按 email 找学生（暂时不在这里用 tutor_id，多租户后面按 student.id 反查）
    student = db.query(Student).filter(Student.email == email).first()

    if not student or not verify_password(plain_password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student account is inactive",
        )

    # 生成带 role="student" 的 token
    access_token = create_access_token({"sub": str(student.id), "role": "student"})
    return Token(access_token=access_token)
