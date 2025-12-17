# App Backend 开发进度记录

> 目录：`app_backend/`  
> 说明：这里只记录 **应用后端（FastAPI）** 的实现进度，便于快速了解当前状态和部署情况。

---

## 1. 运行环境与启动方式

### 1.1 本地开发环境（Windows）

- 虚拟环境：`bac`
  - 路径：`F:\learn\causal\virtual_tutor\app_backend\bac`
  - 启动命令（PowerShell）：
    ```bash
    cd F:\learn\causal\virtual_tutor\app_backend
    .\bac\Scripts\Activate.ps1
    ```
- 运行后端：
  ```bash
  (bac) uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

* 本地访问：

  * 健康检查：`http://localhost:8000/health`
  * Swagger：`http://localhost:8000/docs`

### 1.2 Web 服务器部署环境（51.161.130.234）

* 用户：`ubuntu`
* 代码路径：

  ```bash
  /home/ubuntu/sciolto/virtual_tutor/app_backend
  ```
* Python 环境：使用 miniconda 创建的 `vt_app`

  ```bash
  source ~/miniconda3/etc/profile.d/conda.sh
  conda activate vt_app
  cd ~/sciolto/virtual_tutor/app_backend
  ```
* 依赖安装：

  ```bash
  (vt_app) pip install -r requirements.txt
  ```
* 启动后端（生产测试）：

  ```bash
  (vt_app) uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
* 外网访问（已验证正常）：

  * `http://51.161.130.234:8000/health` → `{"status": "ok"}`
  * `http://51.161.130.234:8000/docs` → Swagger UI 正常打开

---

## 2. 依赖与配置

### 2.1 requirements

当前 `app_backend/requirements.txt` 仅保留后端运行所需依赖，例如：

* Web 框架相关：

  * `fastapi`
  * `uvicorn`
  * `starlette`
  * `anyio`
  * `h11`
  * `httptools`
  * `websockets`
  * `watchfiles`
* ORM & 数据库：

  * `SQLAlchemy`
  * `alembic`
  * `psycopg2-binary`（为后续切到 Postgres 做准备）
* 配置与数据校验：

  * `pydantic`
  * `annotated-types`
  * `python-dotenv`
  * `email-validator`
* 安全相关：

  * `passlib==1.7.4` + `bcrypt==3.2.2`（固定在 3.x 避免与 passlib 的兼容问题）
  * `python-jose`
  * `cryptography`
  * `rsa`
  * `pyasn1`
  * `ecdsa`
* 其它基础依赖：`PyYAML`, `python-dateutil`, `packaging`, `typing-extensions` 等

所有 Jupyter / IPython / Windows 专用包（如 `ipykernel`, `ipython`, `pywin32` 等）已从服务器环境的 requirements 中移除，避免版本和平台问题。

### 2.2 配置系统

* 使用 `.env` + `app/core/config.py` 管理配置。
* 关键配置项：

  * `SECRET_KEY`
  * `DATABASE_URL`（开发阶段为 `sqlite:///./dev.db`）
  * `ACCESS_TOKEN_EXPIRE_MINUTES`
  * `INIT_ADMIN_EMAIL`
  * `INIT_ADMIN_PASSWORD`

---

## 3. 数据库与 ORM 模型（多租户 + 会话）

### 3.1 数据库

* 当前环境使用 SQLite：`dev.db`
* 通过 SQLAlchemy 自动建表。
* 在 Web 服务器上检查表名：

  ```python
  from app.db.session import engine
  from sqlalchemy import inspect
  insp = inspect(engine)
  insp.get_table_names()
  ```

  返回结果为：

  ```text
  ['admins', 'chat_messages', 'sessions', 'students', 'tutors']
  ```

  说明以下五张表已存在。

### 3.2 ORM 模型概览

* ✅ `Admin` 管理员表（`app/models/admin.py`）

  * 字段示例：`id`, `email`, `hashed_password`, `is_active`, `created_at`, `updated_at` 等。
  * 用于 Admin Portal 登录，多租户顶层边界。

* ✅ `Tutor` 表（`app/models/tutor.py`）

  * 字段示例：`id`, `admin_id`, `name`, `description`, `target_language`, `created_at`, `updated_at`。
  * 关键：`admin_id` 外键 → 每个 Tutor 归属一个 Admin。

* ✅ `Student` 学生表（`app/models/student.py`）

  * 字段示例：`id`, `tutor_id`, `email`, `name`, `hashed_password`, `is_active`, `created_at`, `updated_at`。
  * 关键：`tutor_id` 外键 → 学生只属于某一个 Tutor。
  * `is_active` 控制账号启用 / 禁用。

* ✅ `Session` 会话表（`app/models/session.py`）

  * 用于记录一次学生与 Tutor AI 的“上课会话”：

    * `id`
    * `tutor_id`（外键 → `tutors.id`）
    * `student_id`（外键 → `students.id`）
    * `admin_id`（可选，方便按管理员过滤）
    * `engine_session_id`（AI 引擎内部会话 id，可选）
    * `engine_url`（前端应连接的 AI 引擎地址）
    * `engine_token`（前端连接 AI 引擎的临时凭证）
    * `status`（`pending / active / ended`）
    * `started_at`, `ended_at`
  * 说明：目前 `Session` 只负责**元数据和控制面**，用于后续 RAG & AI 引擎联调。

* ✅ `ChatMessage` 会话消息表（`app/models/chat_message.py`）

  * 用于存储会话中的 Q/A 消息（可供审计与历史回放）：

    * `id`
    * `session_id`（外键 → `sessions.id`）
    * `role`：`"student" | "assistant" | "system"`
    * `content`
    * `created_at`
  * 目前只建了基础结构，接口层还未正式使用。

---

## 4. 安全与认证

* ✅ 密码哈希与校验（`app/core/security.py`）

  * 使用 `passlib[bcrypt]`：

    * `get_password_hash(password)` → 存入 `hashed_password`
    * `verify_password(plain, hashed)` → 登录时校验

* ✅ JWT 生成与解析

  * 使用 `python-jose[cryptography]`：

    * `create_access_token(data: dict, expires_delta=...)`
    * `decode_access_token(token: str)` → 返回 payload 或 `None`
  * JWT payload 结构包含：

    * `sub`: 用户 id（Admin 或 Student）
    * `role`: `"admin"` / `"student"`

* ✅ OAuth2 方案与依赖（`app/api/deps.py`）

  * Admin：

    * `oauth2_admin = OAuth2PasswordBearer(tokenUrl="/api/auth/login")`
    * `get_current_admin()`：校验 token & role，并从 DB 获取 Admin。
  * Student：

    * `oauth2_student = OAuth2PasswordBearer(tokenUrl="/api/student/auth/login")`
    * `get_current_student()`：校验 token & role & `is_active`，并从 DB 获取 Student。

---

## 5. 初始数据脚本

* ✅ `app/initial_data.py`

  * 命令：

    ```bash
    (本地 bac 环境) python -m app.initial_data
    (服务器 vt_app 环境) python -m app.initial_data
    ```
  * 功能：

    * 自动创建初始 Admin 账号（若不存在）：

      * `email`: `admin@example.com`
      * `password`: `admin123`
    * 多次运行只会提示 `Admin already exists: admin@example.com`，不会重复创建。

---

## 6. 已实现的业务 API（应用后端）

### 6.1 Admin 认证

* ✅ `POST /api/auth/login`

  * 说明：Admin 登录接口（OAuth2 Password Flow）。
  * 请求：`application/x-www-form-urlencoded`

    * `username`: Admin 邮箱（例如 `admin@example.com`）
    * `password`: 密码（例如 `admin123`）
  * 响应：

    * `access_token`: JWT（`role="admin"`）
    * `token_type`: `"bearer"`

### 6.2 Tutor 管理（Admin 视角）

* ✅ `GET /api/tutors/`

  * 查询当前 Admin 的 Tutor 列表。
  * 仅返回 `admin_id == 当前 Admin.id` 的记录。

* ✅ `POST /api/tutors/`

  * 为当前 Admin 创建新的 Tutor。
  * Body 示例：

    ```json
    {
      "name": "Year 10 Physics Assistant",
      "description": "Physics helper for Year 10 students",
      "target_language": "en"
    }
    ```

### 6.3 学生管理（Admin 视角）

> 路由前缀：`/api/admin/students`（Admin 身份）

* ✅ `POST /api/admin/students/?tutor_id=<id>`

  * 为指定 Tutor 创建学生账号。
  * 会检查该 `tutor_id` 是否属于当前 Admin（多租户保护）。

* ✅ `GET /api/admin/students/?tutor_id=<id>`

  * 列出某个 Tutor 下的所有学生（仅限当前 Admin 自己的 Tutor）。

* ✅ `PATCH /api/admin/students/{student_id}?tutor_id=<id>`

  * 更新学生信息（姓名、启用状态、重置密码）。

### 6.4 学生登录

* ✅ `POST /api/student/auth/login`

  * 说明：学生登录接口。
  * 示例请求体：

    ```json
    {
      "email": "student1@example.com",
      "password": "stu12345",
      "tutor_id": 1
    }
    ```
  * 逻辑：

    * 使用 `tutor_id + email` 确认学生归属；
    * 检查 `is_active` 和密码；
    * 返回带 `role="student"` 的 JWT。

---

## 7. Swagger / 手动测试情况

* ✅ Swagger UI：

  * 本地：`http://localhost:8000/docs`
  * Web 服务器：`http://51.161.130.234:8000/docs`

* Admin 测试流程：

  1. 运行 `python -m app.initial_data`，保证 Admin 存在；
  2. 在 `/docs` 中使用 `POST /api/auth/login` 登录：

     * `username=admin@example.com`
     * `password=admin123`
  3. 拿到 token 后，点击右上角 **Authorize** 完成授权；
  4. 可调用：

     * `GET /api/tutors/`
     * `POST /api/tutors/`
     * `POST /api/admin/students/`
     * `GET /api/admin/students/` 等。

* Student 测试流程：

  1. Admin 先为某个 Tutor 创建学生账号；
  2. 调用 `POST /api/student/auth/login`，使用该学生的 `email + password + tutor_id`；
  3. 成功返回 token，说明学生登录逻辑正常（后续 Session 控制面会基于此）。

---

## 8. 当前暂停点 & 下一步计划（重要）

### ✅ 当前已完成（本轮结束时状态）

* 本地和 Web 服务器上的 FastAPI 应用都可以正常启动；
* Web 服务器上通过公网访问 `/health` 和 `/docs` 正常；
* SQLite 数据库中已有 5 张表：

  * `admins`, `students`, `tutors`, `sessions`, `chat_messages`
* Session / ChatMessage ORM 已创建并建表成功（用于后续会话控制与日志）；
* Admin / Tutor / Student 的认证与基础管理 API 都已经打通；
* 初始 Admin 创建脚本可以在本地和服务器上重复使用。

### Student text chat API

已完成：

- 学生登录后可创建 Session：
  - `POST /api/student/sessions/` → 返回 `id, tutor_id, student_id, status, engine_url, engine_token, started_at`
- 学生可列出自己的 Session：
  - `GET /api/student/sessions/` → 返回当前学生的所有会话列表（按 started_at 倒序）
- 学生在 Session 下发送文本消息：
  - `POST /api/student/sessions/{session_id}/messages`
- 学生查询历史消息：
  - `GET /api/student/sessions/{session_id}/messages`
  - `GET /api/student/sessions/{session_id}` → 附带 `messages` 字段

当前限制 / TODO：

- 目前 `engine_url` / `engine_token` 为 mock 值，未接入真实 AI 引擎
- 消息仅支持纯文本，未接入语音 / avatar 通道
- 未区分 active / ended 的关闭逻辑（后续增加“结束 Session”的接口）

4. **后续（可以放到下一阶段）**

   * 学生历史会话列表 API：`GET /api/student/sessions/`
   * ChatMessage 的落库与查询（后端先预留好接口）
   * 将来对接真实的 AI Infer Engine 管理 API，替换当前 mock 的 `engine_url` / `engine_token`。


