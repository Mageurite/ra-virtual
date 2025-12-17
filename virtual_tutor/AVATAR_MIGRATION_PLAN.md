# Avatar 服务独立部署方案

根据老师的架构设计，Avatar 应该作为独立的 AI Infer Engine（Serverless）部署。

## 🏗️ 目标架构

```
┌─────────────────────────────────────────────────────────────┐
│  Server A - Web Back-End (app_backend/)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FastAPI                                              │  │
│  │  - Admin 登录认证                                     │  │
│  │  - Tutor 管理 (CRUD)                                  │  │
│  │  - Student 管理                                       │  │
│  │  - Avatar 元数据管理 (数据库记录)                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                          ↓ REST API                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Serverless - AI Infer Engine (avatar/)                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FastAPI                                              │  │
│  │  - LLM 聊天推理 (Ollama)                              │  │
│  │  - Avatar 创建/启动 (Mageurite)                       │  │
│  │  - WebRTC 实时通信                                    │  │
│  │  - 无数据库 (Stateless)                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📂 建议的目录结构

### 方案1: 同仓库分离（推荐用于开发阶段）

```
virtual_tutor/
├── app_backend/              # Server A
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_auth.py
│   │   │   ├── routes_tutors.py
│   │   │   └── routes_avatar_metadata.py    # 只管理 Avatar 元数据
│   │   ├── models/
│   │   │   ├── admin.py
│   │   │   ├── tutor.py
│   │   │   └── avatar.py                    # Avatar 元数据（URL、状态等）
│   │   └── main.py
│   └── requirements.txt
│
├── avatar_service/           # Serverless AI Engine
│   ├── llm/
│   │   ├── config.py
│   │   ├── service.py
│   │   └── routes.py                        # POST /chat, /stream
│   ├── avatar/
│   │   ├── config.py
│   │   ├── service.py                       # 与 Mageurite 通信
│   │   └── routes.py                        # POST /create, /start
│   ├── main.py                              # 独立 FastAPI app
│   ├── requirements.txt                     # 只包含 AI 相关依赖
│   └── Dockerfile                           # 独立容器
│
└── frontend/
```

### 方案2: 独立仓库（推荐用于生产部署）

```
# 仓库1: virtual-tutor-backend
app/
  - Admin/Tutor/Student 管理
  - 数据库操作
  - 认证授权

# 仓库2: virtual-tutor-ai-engine
avatar_service/
  - LLM 推理
  - Avatar 生成
  - WebRTC 服务
```

## 🔄 迁移步骤

### 第1步：创建独立的 avatar_service

```bash
cd /Users/murphyxu/Code/ra/virtual_tutor

# 创建独立服务目录
mkdir -p avatar_service/{llm,avatar,api}

# 移动文件
mv app_backend/avatar/llm/* avatar_service/llm/
mv app_backend/avatar/avatar_service/* avatar_service/avatar/
```

### 第2步：移除数据库依赖

**avatar_service/main.py** (新建独立 FastAPI):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llm.routes import router as llm_router
from avatar.routes import router as avatar_router

app = FastAPI(title="Avatar AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "avatar-ai-engine"}

# 只包含 AI 推理相关路由
app.include_router(llm_router, prefix="/api")
app.include_router(avatar_router, prefix="/api")
```

### 第3步：Web Back-End 通过 API 调用

**app_backend/app/api/routes_avatar_proxy.py**:
```python
"""
Avatar Proxy Routes
Web Back-End 作为代理，转发请求到 Avatar AI Engine
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_admin
from app.models.avatar import Avatar

router = APIRouter(prefix="/api/avatars", tags=["avatars"])

AVATAR_SERVICE_URL = "http://avatar-service:8001"  # Serverless 地址

@router.post("/create")
async def create_avatar_proxy(
    tutor_id: int,
    video: UploadFile,
    current_admin: Admin = Depends(get_current_admin)
):
    # 1. 验证权限（Web Back-End 负责）
    tutor = verify_tutor_ownership(tutor_id, current_admin.id)
    
    # 2. 转发到 AI Engine
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AVATAR_SERVICE_URL}/api/avatar/create",
            files={"video": video.file},
            data={"name": f"tutor_{tutor_id}_avatar"}
        )
    
    # 3. 保存元数据到数据库
    avatar = Avatar(
        tutor_id=tutor_id,
        name=response.json()["name"],
        service_url=f"{AVATAR_SERVICE_URL}/api/avatar/{name}",
        status="active"
    )
    db.add(avatar)
    db.commit()
    
    return avatar
```

### 第4步：学生直接访问 AI Engine

学生通过 Tutor URL 直接访问 Serverless AI Engine（无需经过 Web Back-End）:

```
前端 (学生) ──────→ Avatar Service (Serverless)
                   /api/tutors/{id}/chat
                   /api/tutors/{id}/webrtc
```

## 🚀 部署配置

### Docker Compose

```yaml
version: '3.8'

services:
  # Web Back-End (Server A)
  backend:
    build: ./app_backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - AVATAR_SERVICE_URL=http://avatar-service:8001
    depends_on:
      - db
  
  # Avatar AI Engine (Serverless)
  avatar-service:
    build: ./avatar_service
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - MAGEURITE_URL=http://mageurite:8615
    deploy:
      replicas: 3  # 可以水平扩展
  
  # 数据库（只有 backend 访问）
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
```

### Kubernetes (Serverless 部署)

```yaml
# avatar-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: avatar-service
spec:
  replicas: 5  # 自动扩展
  template:
    spec:
      containers:
      - name: avatar-ai
        image: avatar-service:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: avatar-hpa
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## ✅ 优势

1. **符合老师设计** - AI 推理独立为 Serverless
2. **可扩展** - Avatar Service 可以独立水平扩展
3. **无状态** - AI Engine 不需要数据库，易于部署
4. **职责分离** - Web Back-End 管理业务，AI Engine 只做推理
5. **成本优化** - AI 服务可以按需启动/停止（Serverless）

## 🎯 现在要做的

1. **创建独立目录**：`virtual_tutor/avatar_service/`
2. **移动代码**：将 `app_backend/avatar/` 中的 LLM 和 avatar_service 移动过去
3. **移除数据库依赖**：AI Engine 不访问数据库
4. **创建代理 API**：Web Back-End 作为认证和权限网关
5. **更新部署配置**：两个独立服务

需要我帮您开始迁移吗？
