# Virtual Tutor - 架构说明

## 🏗️ 双服务架构

根据老师的设计，系统分为两个独立服务：

```
┌─────────────────────────────────────────────────────────────┐
│  Server A - Web Back-End (app_backend/)                     │
│  Port: 8000                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - Admin 认证和管理                                   │  │
│  │  - Tutor/Student 管理                                 │  │
│  │  - 数据库操作 (PostgreSQL)                            │  │
│  │  - Avatar 元数据管理                                  │  │
│  │  - 代理请求到 Avatar Service                          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP API
┌─────────────────────────────────────────────────────────────┐
│  Serverless - Avatar AI Engine (avatar_service/)            │
│  Port: 8001                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - LLM 推理 (Ollama)                                  │  │
│  │  - Avatar 创建/管理 (Mageurite)                       │  │
│  │  - WebRTC 实时通信                                    │  │
│  │  - 无数据库（完全无状态）                             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📂 目录结构

```
virtual_tutor/
├── app_backend/              # Server A - Web Back-End
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_avatar_admin.py    # 代理：管理员管理 Avatar
│   │   │   ├── routes_avatar_public.py   # 代理：学生访问 Avatar
│   │   │   └── ...其他路由
│   │   ├── models/
│   │   │   ├── admin.py
│   │   │   ├── tutor.py
│   │   │   ├── avatar.py                 # Avatar 元数据
│   │   │   └── ...
│   │   └── main.py
│   └── requirements.txt                  # 只包含 httpx
│
├── avatar_service/           # Serverless - AI Engine
│   ├── llm/                  # LLM 模块
│   ├── avatar/               # Avatar 模块
│   ├── main.py               # 独立 FastAPI
│   └── requirements.txt      # 包含 langchain, httpx
│
└── frontend/                 # React 前端
```

## 🔄 请求流程

### 管理员创建 Avatar

```
1. 前端 → Web Back-End (8000)
   POST /api/admin/avatars/create
   Headers: Authorization: Bearer <jwt>

2. Web Back-End 验证：
   ✓ JWT 认证
   ✓ Tutor 归属检查
   ✓ 数据库查重

3. Web Back-End → Avatar Service (8001)
   POST /api/avatar/create
   (转发视频文件)

4. Avatar Service → Mageurite (8615)
   调用实际的 Avatar 创建

5. Web Back-End 保存元数据到数据库
   Avatar(tutor_id, name, status, engine_url, ...)

6. 返回结果给前端
```

### 学生与 Avatar 对话

```
1. 前端 → Web Back-End (8000)
   POST /api/tutors/123/chat
   (无需认证)

2. Web Back-End 验证：
   ✓ Tutor 存在性检查

3. Web Back-End → Avatar Service (8001)
   POST /api/chat/completion
   (转发消息)

4. Avatar Service → Ollama (11434)
   LLM 推理

5. 流式返回结果
```

## 🚀 启动服务

### Terminal 1: Web Back-End

```bash
cd app_backend

# 配置环境变量
export DATABASE_URL="postgresql://user:pass@localhost:5432/virtual_tutor"
export AVATAR_SERVICE_URL="http://localhost:8001"

# 启动
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Avatar Service

```bash
cd avatar_service

# 配置环境变量
export OLLAMA_BASE_URL="http://localhost:11434"
export LIPSYNC_SERVICE_URL="http://localhost:8615"
export TTS_SERVICE_URL="http://localhost:8604"

# 启动
uvicorn main:app --reload --port 8001
```

### Terminal 3: 外部服务

```bash
# Ollama
ollama serve

# Mageurite Lip-Sync (如果需要)
cd ../mageurite_virtual_tutor/lip-sync
python live_server.py

# Mageurite TTS (如果需要)
cd ../mageurite_virtual_tutor/tts
python tts.py
```

## 📡 API 端点

### Web Back-End (8000)

**管理员 API** (需要认证):
- `POST /api/admin/avatars/create` - 创建 Avatar
- `GET /api/admin/avatars/list` - 列出 Avatars
- `POST /api/admin/avatars/{id}/start` - 启动 Avatar
- `DELETE /api/admin/avatars/{id}` - 删除 Avatar

**学生公开 API** (无需认证):
- `GET /api/tutors/{id}/info` - Tutor 信息
- `POST /api/tutors/{id}/chat` - 聊天
- `POST /api/tutors/{id}/chat/stream` - 流式聊天
- `GET /api/tutors/{id}/avatar/preview` - 预览图
- `POST /api/tutors/{id}/webrtc/*` - WebRTC

### Avatar Service (8001)

**LLM API**:
- `POST /api/chat/completion` - 非流式聊天
- `POST /api/chat/stream` - 流式聊天
- `GET /api/chat/models` - 可用模型

**Avatar API**:
- `POST /api/avatar/create` - 创建 Avatar
- `GET /api/avatar/list` - 列出 Avatars
- `POST /api/avatar/start` - 启动 Avatar
- `GET /api/avatar/preview/{name}` - 预览图
- `DELETE /api/avatar/delete` - 删除 Avatar

## 🔒 安全说明

1. **认证由 Web Back-End 处理** - Avatar Service 不需要认证
2. **权限检查由 Web Back-End 处理** - 确保 Tutor 归属
3. **数据库只有 Web Back-End 访问** - Avatar Service 完全无状态
4. **Web Back-End 作为网关** - 所有外部请求先经过它

## 🐳 Docker 部署

```yaml
version: '3.8'

services:
  web-backend:
    build: ./app_backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/virtual_tutor
      - AVATAR_SERVICE_URL=http://avatar-service:8001
    depends_on:
      - db
  
  avatar-service:
    build: ./avatar_service
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LIPSYNC_SERVICE_URL=http://mageurite:8615
  
  db:
    image: postgres:15
```

## ✅ 关键优势

1. **职责分离** - Web Back-End 管业务，Avatar Service 管 AI
2. **可扩展** - Avatar Service 可以独立水平扩展
3. **无状态** - Avatar Service 随时可以重启
4. **解耦** - virtual-tutor 和 mageurite 完全解耦
5. **灵活部署** - 两个服务可以部署在不同服务器
