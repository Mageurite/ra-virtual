from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.admin import Admin
from app.models.student import Student
from app.core.security import decode_access_token

oauth2_admin = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="AdminOAuth2",
)
oauth2_student = OAuth2PasswordBearer(
    tokenUrl="/api/student/auth/login",
    scheme_name="StudentOAuth2",
)


def get_current_admin(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_admin),
) -> Admin:
    """从 Bearer Token 中解析出当前 Admin"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None or payload.get("role") != "admin":
        raise credentials_exception

    # 我们在生成 token 时会写入 'sub' 字段为 admin_id
    sub = payload.get("sub")
    try:
        admin_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        raise credentials_exception

    return admin

def get_current_student(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_student),
) -> Student:
    """从 Bearer Token 中解析出当前 Student"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate student credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None or payload.get("role") != "student":
        raise credentials_exception

    # 我们在生成 token 时会写入 'sub' 字段为 student_id
    sub = payload.get("sub")
    try:
        student_id = int(sub)
    except (TypeError, ValueError):
        raise credentials_exception

    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None or not student.is_active:
        raise credentials_exception

    return student

