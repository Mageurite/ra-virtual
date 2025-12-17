from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.admin import Admin
from app.models.student import Student
from app.models.tutor import Tutor
from app.schemas.student import StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/api/admin/students", tags=["admin-students"])


@router.post("/", response_model=StudentOut)
def create_student_for_tutor(
    tutor_id: int,
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    # 确保这个 tutor 属于当前 admin（多租户保护）
    tutor = (
        db.query(Tutor)
        .filter(Tutor.id == tutor_id, Tutor.admin_id == current_admin.id)
        .first()
    )
    if tutor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found or not owned by current admin",
        )

    hashed_password = get_password_hash(student_in.password)
    student = Student(
        tutor_id=tutor.id,
        email=student_in.email,
        name=student_in.name,
        hashed_password=hashed_password,
        is_active=student_in.is_active,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/", response_model=List[StudentOut])
def list_students_for_tutor(
    tutor_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    # 先验证 tutor 归属
    tutor = (
        db.query(Tutor)
        .filter(Tutor.id == tutor_id, Tutor.admin_id == current_admin.id)
        .first()
    )
    if tutor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found or not owned by current admin",
        )

    students = (
        db.query(Student)
        .filter(Student.tutor_id == tutor.id)
        .order_by(Student.id.desc())
        .all()
    )
    return students


@router.patch("/{student_id}", response_model=StudentOut)
def update_student(
    tutor_id: int,
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    # 先保证 tutor 属于当前 admin
    tutor = (
        db.query(Tutor)
        .filter(Tutor.id == tutor_id, Tutor.admin_id == current_admin.id)
        .first()
    )
    if tutor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found or not owned by current admin",
        )

    student = (
        db.query(Student)
        .filter(Student.id == student_id, Student.tutor_id == tutor.id)
        .first()
    )
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    if student_in.name is not None:
        student.name = student_in.name
    if student_in.is_active is not None:
        student.is_active = student_in.is_active
    if student_in.password:
        student.hashed_password = get_password_hash(student_in.password)

    db.add(student)
    db.commit()
    db.refresh(student)
    return student
