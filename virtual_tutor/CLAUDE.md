# Virtual Tutor - Claude Development Log

## 项目概述

Virtual Tutor 是一个多租户虚拟导师系统，支持 AI 驱动的 Avatar 对话功能。

**核心架构**：
- **Server A**（不封装 Docker）：Web Frontend + Web Backend（业务逻辑、数据库）
- **Serverless**（封装 Docker）：AI Infer Engine（Avatar Service + Lip-Sync + TTS）

---

## 最新变更（2025-12-18）

### ✅ 完成的功能

#### 1. 统一的 Create Tutor API
**位置**：`app_backend/app/api/routes_tutors.py`

**端点**：`POST /api/tutors/create-with-avatar`

**功能**：
- 一次性创建 Tutor + Avatar
- 完整的事务管理（失败自动回滚）
- 文件大小限制（视频 100MB，音频 50MB）
- 竞态条件保护（提前检查 Avatar 名称）
- 完善的错误处理和清理逻辑

**请求格式**：
```http
POST /api/tutors/create-with-avatar
Content-Type: multipart/form-data

# Tutor fields
name: string (required)
description: string (optional)
target_language: string (default: "en")

# Avatar fields
avatar_name: string (required, unique)
avatar_model: string (default: "MuseTalk")
tts_model: string (default: "edge-tts")
timbre: string (optional)
avatar_blur: boolean (default: false)
support_clone: boolean (default: false)
ref_text: string (optional)

# Files
prompt_face: file (required, video)
prompt_voice: file (optional, audio)
```

**响应格式**：
```json
{
  "status": "success",
  "message": "Tutor 'xxx' with avatar 'yyy' created successfully",
  "tutor": {
    "id": 1,
    "name": "Test Tutor",
    "description": "...",
    "target_language": "en",
    "created_at": "2025-12-18T..."
  },
  "avatar": {
    "id": 1,
    "name": "avatar_001",
    "avatar_model": "MuseTalk",
    "tts_model": "edge-tts",
    "status": "active",
    "preview_image_path": "/path/to/image.png"
  }
}
```

#### 2. Frontend 表单完善
**位置**：`frontend/src/components/admin/TutorsPage.js`

**新增字段**：
- Avatar 模型选择（MuseTalk/Wav2Lip/UltraLight）
- TTS 模型选择（Edge TTS/CosyVoice/SoVITS）
- 语音音色配置
- 模糊效果开关
- 声音克隆开关
- 视频文件上传（必需）
- 音频文件上传（克隆时必需）

**用户体验优化**：
- 实时进度显示
- 文件大小验证
- 表单验证
- 创建进度提示（2-5 分钟）
- 成功/失败提示

#### 3. WebRTC 代理修复
**位置**：`avatar_service/avatar/routes.py`

**问题**：WebRTC 代理未正确转发 POST 请求体

**修复**：
```python
@router.api_route("/webrtc/{path:path}", ...)
async def webrtc_proxy(path: str, request: Request):
    # 正确处理请求体
    body = None
    if request.method in ["POST", "PUT"]:
        body = await request.body()
    
    response = await client.request(
        method=request.method,
        url=webrtc_url,
        content=body,
        headers={...}
    )
```

#### 4. 错误处理增强

**文件大小限制**：
```python
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB
```

**竞态条件防护**：
- 创建 Tutor 前先检查 Avatar 名称
- 避免创建后发现冲突导致回滚

**事务完整性**：
- Avatar Service 失败 → 回滚 Tutor
- 数据库保存失败 → 回滚 Tutor + 记录孤儿 Avatar
- 所有异常路径都有清理逻辑

---

## 架构设计

### 职责分离

```
┌─────────────────────────────────────┐
│ Server A (不封装 Docker)             │
├─────────────────────────────────────┤
│ Web Frontend (React)                │
│  - Admin 管理界面                    │
│  - Student 学习界面                  │
│                                     │
│ Web Backend (FastAPI)               │
│  - 业务逻辑                          │
│  - 数据库操作 (PostgreSQL)           │
│  - 权限验证                          │
│  - 代理 AI 请求                      │
└─────────────────────────────────────┘
              ↓ HTTP
┌─────────────────────────────────────┐
│ Serverless (封装 Docker, 可扩展)      │
├─────────────────────────────────────┤
│ Avatar Service (8001)               │
│  - LLM 推理调度                      │
│  - Avatar 管理调度                   │
│  - TTS 调度                         │
│  - 无数据库依赖                      │
│                                     │
│ Lip-Sync Service (8615)             │
│  - Avatar 模型生成 (GPU 密集)        │
│  - 视频处理                          │
│  - WebRTC 视频流                     │
│                                     │
│ TTS Service (8604)                  │
│  - 语音合成                          │
│  - 多引擎支持                        │
└─────────────────────────────────────┘
```

### 数据流：创建 Tutor+Avatar

```
Frontend
  ↓ POST /api/tutors/create-with-avatar
  
Web Backend (routes_tutors.py)
  ├─ 1. 验证文件大小
  ├─ 2. 检查 Avatar 名称冲突
  ├─ 3. 创建 Tutor 记录 (PostgreSQL)
  ├─ 4. 调用 Avatar Service ─────────→ Avatar Service (8001)
  │                                      ↓ POST /api/avatar/create
  │                                    Avatar Service
  │                                      ↓ 转发到 Lip-Sync
  │                                    Lip-Sync Service (8615)
  │                                      ├─ 处理视频文件
  │                                      ├─ 生成 Avatar 模型
  │                                      └─ 返回预览图
  │                                    ← 返回结果
  ├─ 5. 保存 Avatar 元数据 (PostgreSQL)
  └─ 6. 返回完整结果

← 成功响应
```

---

## API 路由总览

### Web Backend (app_backend/)

#### Tutor 管理 (`routes_tutors.py`)
```
POST   /api/tutors/                    创建 Tutor（简单）
GET    /api/tutors/                    列出 Tutors
POST   /api/tutors/create-with-avatar  创建 Tutor+Avatar（推荐）✨
```

#### 公开访问 (`routes_avatar_public.py`)
```
GET    /api/tutors/{id}/info           获取 Tutor 信息
POST   /api/tutors/{id}/chat           聊天对话
POST   /api/tutors/{id}/chat/stream    流式聊天
GET    /api/tutors/{id}/avatar/preview Avatar 预览图
GET    /api/tutors/{id}/health         健康检查
ALL    /api/tutors/{id}/webrtc/{path}  WebRTC 代理
```

#### Admin 管理 (`routes_avatar_admin.py`)
```
POST   /api/admin/avatars/create       创建 Avatar（单独）
POST   /api/admin/avatars/{id}/start   启动 Avatar
POST   /api/admin/avatars/{id}/stop    停止 Avatar
GET    /api/admin/avatars/             列出 Avatars
DELETE /api/admin/avatars/{id}         删除 Avatar
```

### Avatar Service (avatar_service/)

#### Avatar 管理 (`avatar/routes.py`)
```
GET    /api/avatar/list                列出所有 avatars
POST   /api/avatar/create              创建 avatar
POST   /api/avatar/start               启动 avatar
GET    /api/avatar/preview/{name}      获取预览图
DELETE /api/avatar/delete              删除 avatar
GET    /api/avatar/tts-models          TTS 模型列表
GET    /api/avatar/avatar-models       Avatar 模型列表
GET    /api/avatar/health              健康检查
ALL    /api/avatar/webrtc/{path}       WebRTC 代理
```

#### LLM 服务 (`llm/routes.py`)
```
POST   /api/chat/completion            聊天对话
POST   /api/chat/stream                流式聊天
POST   /api/chat/rag                   RAG 增强对话
```

#### TTS 服务 (`tts/routes.py`)
```
POST   /api/tts/synthesize-json        语音合成
POST   /api/tts/synthesize-stream      流式语音合成
GET    /api/tts/models                 TTS 模型列表
```

---

## 环境变量配置

### Web Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/virtual_tutor

# Security
SECRET_KEY=your-secret-key-here

# Services
AVATAR_SERVICE_URL=http://localhost:8001

# CORS
FRONTEND_URL=http://localhost:3000
```

### Avatar Service (.env)

```bash
# LLM Service
OLLAMA_BASE_URL=http://localhost:11434

# Internal Services (封装在 Docker 内)
LIPSYNC_SERVICE_URL=http://localhost:8615  # 或 Docker: http://lip-sync:8615
TTS_SERVICE_URL=http://localhost:8604      # 或 Docker: http://tts:8604

# Models
DEFAULT_AVATAR_MODEL=MuseTalk
DEFAULT_TTS_MODEL=edge-tts
```

### Lip-Sync Service (.env)

```bash
# Optional: GPU device
GPU_DEVICE=0

# Optional: Model paths
MODEL_PATH=/path/to/models
```

### TTS Service (.env)

```bash
# Optional: Model paths
TTS_MODEL_PATH=/path/to/tts/models
TTS_CACHE_DIR=/path/to/cache
```

---

## 部署架构

### 开发环境（本地）

```bash
# Terminal 1: Web Backend
cd app_backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Avatar Service
cd avatar_service
uvicorn main:app --reload --port 8001

# Terminal 3: Lip-Sync Service
cd services/lip-sync
python live_server.py

# Terminal 4: TTS Service
cd services/tts
python tts.py

# Terminal 5: Frontend
cd frontend
npm start
```

### 生产环境（Docker）

**Server A**（Web Backend + Frontend）：
```bash
# Web Backend (不打包 Docker)
cd app_backend
gunicorn app.main:app -c gunicorn_config.py

# Frontend (Nginx 静态托管)
cd frontend
npm run build
# Deploy to Nginx
```

**Serverless**（Avatar Service + 内部服务）：
```yaml
# docker-compose.yml
version: '3.8'

services:
  avatar-service:
    build: ./avatar_service
    ports:
      - "8001:8001"
    environment:
      - LIPSYNC_SERVICE_URL=http://lip-sync:8615
      - TTS_SERVICE_URL=http://tts:8604
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    depends_on:
      - lip-sync
      - tts
  
  lip-sync:
    build: ./services/lip-sync
    ports:
      - "8615:8615"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./data/avatars:/app/data
  
  tts:
    build: ./services/tts
    ports:
      - "8604:8604"
    volumes:
      - ./data/tts:/app/cache
```

启动：
```bash
docker-compose up -d
```

---

## 数据库模型

### Tutor
```python
class Tutor(Base):
    id: int
    admin_id: int                # Foreign key
    name: str
    description: str (optional)
    target_language: str
    created_at: datetime
```

### Avatar
```python
class Avatar(Base):
    id: int
    tutor_id: int                # Foreign key
    name: str (unique)
    display_name: str
    avatar_model: str            # MuseTalk, wav2lip, ultralight
    tts_model: str               # edge-tts, cosyvoice, sovits
    timbre: str (optional)
    avatar_blur: bool
    support_clone: bool
    status: str                  # active, inactive, processing, error
    preview_image_path: str
    video_path: str
    audio_path: str
    engine_url: str              # Avatar Service URL
    created_at: datetime
    updated_at: datetime
```

---

## 已知问题和注意事项

### 1. 文件存储
**现状**：本地文件路径  
**建议**：使用对象存储（S3/OSS）或共享存储（NFS）

### 2. 并发限制
**现状**：数据库 unique 约束  
**建议**：添加分布式锁（Redis）防止并发创建相同名称

### 3. Avatar 清理
**现状**：Avatar Service 失败可能留下孤儿文件  
**建议**：定期清理任务或手动删除

### 4. 超时配置
**现状**：Avatar 创建 300 秒  
**建议**：根据硬件调整，或改为异步任务

### 5. GPU 资源
**现状**：单 GPU 同步处理  
**建议**：队列系统 + 多 GPU 支持

---

## 测试清单

### API 测试
```bash
# 1. 创建 Tutor+Avatar
curl -X POST http://localhost:8000/api/tutors/create-with-avatar \
  -H "Authorization: Bearer $TOKEN" \
  -F "name=Test Tutor" \
  -F "description=Test" \
  -F "target_language=en" \
  -F "avatar_name=test_avatar" \
  -F "avatar_model=MuseTalk" \
  -F "tts_model=edge-tts" \
  -F "avatar_blur=false" \
  -F "support_clone=false" \
  -F "prompt_face=@video.mp4"

# 2. 列出 Tutors
curl http://localhost:8000/api/tutors/ \
  -H "Authorization: Bearer $TOKEN"

# 3. 获取 Tutor 信息
curl http://localhost:8000/api/tutors/1/info

# 4. 聊天测试
curl -X POST http://localhost:8000/api/tutors/1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "conversation_history": []}'

# 5. 健康检查
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Frontend 测试
1. 访问 Admin 界面：`http://localhost:3000/admin/tutors`
2. 点击 "Create Tutor"
3. 填写表单并上传文件
4. 等待 2-5 分钟
5. 验证创建成功

---

## 性能优化建议

### 1. 异步任务队列
使用 Celery 或 RQ 处理 Avatar 创建：
```python
@celery.task
def create_avatar_task(tutor_id, avatar_data):
    # 异步处理
    pass
```

### 2. 缓存层
Redis 缓存常用数据：
```python
@cache.memoize(timeout=300)
def get_tutor_info(tutor_id):
    return db.query(Tutor).get(tutor_id)
```

### 3. CDN 加速
静态资源和预览图使用 CDN

### 4. 负载均衡
Avatar Service 多实例 + Nginx 负载均衡

---

## 更新日志

### 2025-12-18
- ✅ 实现统一的 Create Tutor+Avatar API
- ✅ 前端表单完善（Avatar 配置）
- ✅ 修复 WebRTC 代理请求体转发问题
- ✅ 添加文件大小限制和验证
- ✅ 改进错误处理和事务管理
- ✅ 修复竞态条件问题
- ✅ 完善配置文档

### 待办事项
- [ ] 异步任务队列
- [ ] 对象存储集成
- [ ] 分布式锁
- [ ] 监控和日志系统
- [ ] 自动化测试

---

## 技术栈

### Backend
- FastAPI 0.104+
- SQLAlchemy 2.0
- PostgreSQL 15
- httpx (异步 HTTP 客户端)
- Pydantic 2.0

### Frontend
- React 18
- Material-UI 5
- Axios
- React Router 6

### AI Services
- Ollama (LLM)
- MuseTalk/Wav2Lip (Avatar)
- Edge TTS/CosyVoice/SoVITS (TTS)
- PyTorch (GPU 加速)

### Infrastructure
- Docker / Docker Compose
- Nginx
- Gunicorn
- WebRTC

---

## 联系和支持

有问题请查看：
- [README.md](README.md) - 快速开始
- [DEPLOYMENT.md](DEPLOYMENT.md) - 部署指南
- [API_VERIFICATION.md](API_VERIFICATION.md) - API 验证报告
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构文档
