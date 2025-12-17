"""
Functional test: student text chat flow

前提：
- 后端已经在本机或服务器上跑起来
- 数据库里已经有一个可用的学生账号（is_active = True）
- 学生登录接口已经打通

用法：
    cd /home/ubuntu/sciolto/virtual_tutor/app_backend
    VT_APP_BASE_URL="http://51.161.130.234:8000" \
    VT_TEST_STUDENT_USERNAME="student1@example.com" \
    VT_TEST_STUDENT_PASSWORD="stu12345" \
    pytest -q tests/test_student_text_chat.py
"""

import os
import uuid
from typing import Dict

import pytest
import requests


# ----------------------------
# 配置区：可以用环境变量覆盖
# ----------------------------

BASE_URL = os.environ.get("VT_APP_BASE_URL", "http://51.161.130.234:8000")

# 这里用环境变量可以避免把真实账号写死在仓库里
STUDENT_USERNAME = os.environ.get("VT_TEST_STUDENT_USERNAME", "student1@example.com")
STUDENT_PASSWORD = os.environ.get("VT_TEST_STUDENT_PASSWORD", "stu12345")

# 学生登录接口路径（如果你项目里路径不同，只改这里）
STUDENT_LOGIN_PATH = os.environ.get(
    "VT_STUDENT_LOGIN_PATH",
    "/api/student/auth/login",  # 如果你用的是 /api/auth/student/login，就改成那个
)


def _full_url(path: str) -> str:
    """拼出完整 URL，避免重复写 BASE_URL。"""
    return BASE_URL.rstrip("/") + path


def login_student() -> Dict[str, str]:
    """
    用学生账号登录，返回带 Authorization 的 headers。
    """
    resp = requests.post(
        _full_url(STUDENT_LOGIN_PATH),
        data={
            "username": STUDENT_USERNAME,
            "password": STUDENT_PASSWORD,
        },
        # OAuth2PasswordRequestForm 要求表单编码
        timeout=10,
    )
    assert resp.status_code == 200, (
        f"Student login failed: {resp.status_code}, body={resp.text}"
    )
    data = resp.json()
    assert "access_token" in data, f"Unexpected login response: {data}"
    token = data["access_token"]
    token_type = data.get("token_type", "bearer")
    return {"Authorization": f"{token_type.capitalize()} {token}"}


@pytest.mark.functional
def test_student_text_chat_flow():
    """
    完整流程：
    1. 学生登录拿到 JWT
    2. 创建一个新的 Session
    3. 在该 Session 下发送一条消息
    4. 用 messages 列表接口查到这条消息
    5. 用 Session 详情接口查到这条消息
    """
    # 1. 登录
    headers = login_student()

    # 2. 创建 Session
    create_session_resp = requests.post(
        _full_url("/api/student/sessions/"),
        json={},  # SessionCreate 当前是空模型
        headers=headers,
        timeout=10,
    )
    assert create_session_resp.status_code in (200, 201), (
        f"Create session failed: {create_session_resp.status_code}, "
        f"body={create_session_resp.text}"
    )
    session_data = create_session_resp.json()
    assert "id" in session_data, f"Unexpected session response: {session_data}"
    session_id = session_data["id"]

    # 3. 在这个 Session 下发送一条消息
    unique_text = f"Hello from functional test {uuid.uuid4()}"
    send_msg_resp = requests.post(
        _full_url(f"/api/student/sessions/{session_id}/messages"),
        json={
            "role": "student",
            "content": unique_text,
        },
        headers=headers,
        timeout=10,
    )
    assert send_msg_resp.status_code == 200, (
        f"Send message failed: {send_msg_resp.status_code}, "
        f"body={send_msg_resp.text}"
    )
    msg_data = send_msg_resp.json()
    assert msg_data.get("session_id") == session_id, msg_data
    assert msg_data.get("content") == unique_text, msg_data
    assert msg_data.get("role") == "student", msg_data

    # 4. 用 messages 列表接口查该 Session 的所有消息
    list_msgs_resp = requests.get(
        _full_url(f"/api/student/sessions/{session_id}/messages"),
        headers=headers,
        timeout=10,
    )
    assert list_msgs_resp.status_code == 200, (
        f"List messages failed: {list_msgs_resp.status_code}, "
        f"body={list_msgs_resp.text}"
    )
    msgs = list_msgs_resp.json()
    assert isinstance(msgs, list), f"Expected list, got: {type(msgs)}"
    assert any(m.get("content") == unique_text for m in msgs), (
        "Message not found in /messages list",
        msgs,
    )

    # 5. 用 Session 详情接口（带 messages）再确认一次
    detail_resp = requests.get(
        _full_url(f"/api/student/sessions/{session_id}"),
        headers=headers,
        timeout=10,
    )
    assert detail_resp.status_code == 200, (
        f"Get session detail failed: {detail_resp.status_code}, "
        f"body={detail_resp.text}"
    )
    detail = detail_resp.json()
    assert detail.get("id") == session_id, detail
    messages = detail.get("messages", [])
    assert isinstance(messages, list), f"detail.messages is not a list: {messages}"
    assert any(m.get("content") == unique_text for m in messages), (
        "Message not found in session detail.messages",
        messages,
    )
