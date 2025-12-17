from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.session import Session as SessionModel
from app.models.student import Student as StudentModel
from app.models.chat_message import ChatMessage

from app.schemas.session import (
    SessionOut, 
    SessionCreate,
    SessionWithMessages,
)

from app.schemas.chat_message import (
    ChatMessageCreate,
    ChatMessageOut,
)

router = APIRouter(
    prefix="/api/student/sessions",
    tags=["student-sessions"],
)


@router.post("/", response_model=SessionOut)
def create_session_for_student(
    _: SessionCreate,  # 目前不需要 body，可保留占位，方便后续扩展
    db: Session = Depends(deps.get_db),
    current_student: StudentModel = Depends(deps.get_current_student),
):
    """
    学生端创建一个新的 Session。
    - 使用当前登录学生的 tutor_id / student_id
    - 生成一条 Session 记录
    - 暂时 mock 一个 engine_url / engine_token 返回给前端
    """

    if not current_student.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student account is not active.",
        )

    # 从当前学生获取 tutor_id / student_id
    tutor_id = current_student.tutor_id
    student_id = current_student.id

    # 这里先 mock 引擎的信息，后面拿到真实 AI 引擎文档后再替换
    mock_engine_url = "wss://mock-ai-engine.example.com/session/123"
    mock_engine_token = "dummy-token-123"

    db_session = SessionModel(
        tutor_id=tutor_id,
        student_id=student_id,
        # 如果你的 Session 模型里有 admin_id 且允许为 NULL，可以先不填
        status="active",
        engine_url=mock_engine_url,
        engine_token=mock_engine_token,
        started_at=datetime.utcnow(),
    )

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return db_session

# 鉴权 & 拿 Session
def _get_session_for_student(
    db: Session,
    session_id: int,
    student_id: int,
) -> SessionModel:
    """
    确保 session 属于当前学生；否则抛 404。
    """
    session_obj = (
        db.query(SessionModel)
        .filter(
            SessionModel.id == session_id,
            SessionModel.student_id == student_id,
        )
        .first()
    )
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session_obj

# Session 详情，带消息列表
@router.get("/{session_id}", response_model=SessionWithMessages)
def get_session_detail(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_student: StudentModel = Depends(deps.get_current_student),
):
    """
    学生端获取某个 Session 的详情，包括消息列表。
    """
    session_obj = _get_session_for_student(db, session_id, current_student.id)
    return session_obj

# 列出消息
@router.get("/{session_id}/messages", response_model=list[ChatMessageOut])
def list_messages(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_student: StudentModel = Depends(deps.get_current_student),
):
    """
    列出当前学生某个 Session 的所有消息（按时间升序）。
    """
    # 先确认 Session 属于当前学生
    _ = _get_session_for_student(db, session_id, current_student.id)

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return msgs

# 发送一条消息
@router.post("/{session_id}/messages", response_model=ChatMessageOut)
def send_message(
    session_id: int,
    msg_in: ChatMessageCreate,
    db: Session = Depends(deps.get_db),
    current_student: StudentModel = Depends(deps.get_current_student),
):
    """
    学生在某个 Session 下发送一条消息。
    目前只写入 chat_messages，不调用真实 LLM。
    """
    session_obj = _get_session_for_student(db, session_id, current_student.id)

    # 也可以在这里强制 role="student"，避免前端乱传
    role = msg_in.role or "student"

    msg = ChatMessage(
        session_id=session_obj.id,
        role=role,
        content=msg_in.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

# 列出当前学生所有 Session
@router.get("/", response_model=List[SessionOut])
def list_sessions_for_student(
    db: Session = Depends(deps.get_db),
    current_student: StudentModel = Depends(deps.get_current_student),
):
    """
    学生端：列出当前学生的所有 Session（按时间倒序）。
    以后前端可以用它展示“历史会话列表”。
    """
    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.student_id == current_student.id)
        .order_by(SessionModel.started_at.desc())
        .all()
    )
    return sessions

