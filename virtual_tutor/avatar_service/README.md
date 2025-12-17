# Avatar Service - 独立的 AI 推理引擎

## 🎯 服务说明

这是一个独立的 Serverless AI 推理服务，提供：
- **LLM 聊天推理** (基于 Ollama)
- **Avatar 创建和管理** (基于 Mageurite)
- **WebRTC 实时通信**

**无数据库依赖** - 完全无状态，可以水平扩展

## 📁 目录结构

```
avatar_service/
├── main.py                  # FastAPI 应用入口
├── requirements.txt         # Python 依赖
├── Dockerfile              # Docker 镜像
├── .env.example            # 环境变量模板
├── llm/                    # LLM 模块
│   ├── config.py           # Ollama 配置
│   ├── service.py          # LLM 服务实现
│   └── routes.py           # LLM API 路由
├── avatar/                 # Avatar 模块
│   ├── config.py           # Mageurite 配置
│   ├── service.py          # Avatar 服务客户端
│   └── routes.py           # Avatar API 路由
└── tests/                  # 测试文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd avatar_service
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 Ollama 和 Mageurite 服务地址
```

### 3. 启动服务

```bash
# 开发环境
uvicorn main:app --reload --port 8001

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### 4. 访问 API 文档

打开浏览器：http://localhost:8001/docs

## 📡 API 端点

### LLM Chat API (`/api/chat`)

```bash
# 非流式聊天
POST /api/chat/completion
Body: {
  "message": "What is 2+2?",
  "conversation_history": []
}

# 流式聊天 (SSE)
POST /api/chat/stream
Body: {
  "message": "Tell me a story",
  "conversation_history": []
}

# 获取可用模型
GET /api/chat/models

# 健康检查
GET /api/chat/health
```

### Avatar API (`/api/avatar`)

```bash
# 列出 Avatars
GET /api/avatar/list

# 创建 Avatar
POST /api/avatar/create
FormData:
  - name: "avatar_name"
  - prompt_face: <video_file>
  - avatar_model: "MuseTalk"
  - tts_model: "edge-tts"

# 启动 Avatar
POST /api/avatar/start
FormData:
  - avatar_name: "avatar_name"

# 获取预览图
GET /api/avatar/preview/{avatar_name}

# 删除 Avatar
DELETE /api/avatar/delete
FormData:
  - avatar_name: "avatar_name"

# WebRTC 代理
POST /api/avatar/webrtc/{path}

# 健康检查
GET /api/avatar/health
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t avatar-service:latest .
```

### 运行容器

```bash
docker run -d \
  --name avatar-service \
  -p 8001:8001 \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e LIPSYNC_SERVICE_URL=http://mageurite:8615 \
  -e TTS_SERVICE_URL=http://mageurite:8604 \
  avatar-service:latest
```

### Docker Compose

```yaml
version: '3.8'

services:
  avatar-service:
    build: ./avatar_service
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LIPSYNC_SERVICE_URL=http://mageurite:8615
      - TTS_SERVICE_URL=http://mageurite:8604
    restart: unless-stopped
```

## 🔗 与 Web Back-End 集成

Web Back-End (Server A) 可以通过 HTTP 调用此服务：

```python
# app_backend/app/services/avatar_client.py
import httpx

AVATAR_SERVICE_URL = "http://avatar-service:8001"

async def create_avatar_for_tutor(tutor_id: int, video: bytes):
    """代理到 Avatar Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AVATAR_SERVICE_URL}/api/avatar/create",
            files={"prompt_face": video},
            data={"name": f"tutor_{tutor_id}_avatar"}
        )
    return response.json()
```

## ⚙️ 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | `8001` |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | `http://localhost:11434` |
| `LLM_DEFAULT_MODEL` | 默认 LLM 模型 | `mistral-nemo:12b-instruct-2407-fp16` |
| `LIPSYNC_SERVICE_URL` | Lip-Sync 服务地址 | `http://localhost:8615` |
| `TTS_SERVICE_URL` | TTS 服务地址 | `http://localhost:8604` |

## 🧪 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/ -v
```

## 📊 架构优势

✅ **无状态** - 不依赖数据库，可以随意扩展  
✅ **Serverless 友好** - 可以部署到 AWS Lambda、Google Cloud Functions 等  
✅ **水平扩展** - 可以启动多个实例处理高并发  
✅ **职责单一** - 只负责 AI 推理，不处理业务逻辑  
✅ **独立部署** - 与 Web Back-End 解耦，可以独立升级

## 🔒 安全建议

1. **API Key 认证** - 添加 API Key 验证
2. **速率限制** - 防止滥用
3. **CORS 配置** - 限制允许的来源
4. **输入验证** - 严格验证用户输入

## 📝 注意事项

- 此服务**不直接访问数据库**
- 所有用户认证和权限由 Web Back-End 处理
- Avatar 元数据（归属、状态等）存储在 Web Back-End
- 此服务只负责 AI 推理和 Avatar 物理操作
