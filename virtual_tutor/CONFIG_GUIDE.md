# 🔧 Virtual Tutor 配置指南

本文档详细说明所有配置项和环境变量。

---

## 📁 配置文件位置

```
virtual_tutor/
├── app_backend/
│   ├── .env                    # Web Backend 配置（需创建）
│   └── .env.example            # 配置模板
├── avatar_service/
│   ├── .env                    # Avatar Service 配置（需创建）
│   └── .env.example            # 配置模板
├── services/
│   ├── lip-sync/
│   │   └── lip-sync.json       # Lip-Sync 配置
│   └── tts/
│       └── config.json         # TTS 配置（可选）
└── frontend/
    └── .env.local              # Frontend 配置（需创建）
```

---

## 🌐 Web Backend 配置

### 文件：`app_backend/.env`

```bash
# =============================================================================
# 数据库配置
# =============================================================================

# PostgreSQL 连接字符串
DATABASE_URL=postgresql://vtutor_user:your_password@localhost:5432/virtual_tutor

# SQLite (开发测试)
# DATABASE_URL=sqlite:///./virtual_tutor.db

# =============================================================================
# 安全配置
# =============================================================================

# JWT 密钥（必须修改为随机字符串）
SECRET_KEY=your-super-secret-key-change-in-production

# JWT 过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# =============================================================================
# 服务配置
# =============================================================================

# Avatar Service URL（Serverless AI Engine）
AVATAR_SERVICE_URL=http://localhost:8001

# Docker 部署时使用服务名
# AVATAR_SERVICE_URL=http://avatar-service:8001

# 远程部署时使用 IP/域名
# AVATAR_SERVICE_URL=http://192.168.1.100:8001

# =============================================================================
# CORS 配置
# =============================================================================

# 允许的前端地址（逗号分隔）
FRONTEND_URL=http://localhost:3000,http://localhost:8080

# 生产环境
# FRONTEND_URL=https://your-domain.com,https://avatar.your-domain.com

# =============================================================================
# 应用配置
# =============================================================================

# 项目名称
PROJECT_NAME=Virtual Tutor

# 调试模式
DEBUG=true

# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# =============================================================================
# 文件上传限制
# =============================================================================

# 最大视频文件大小（字节）
MAX_VIDEO_SIZE=104857600  # 100MB

# 最大音频文件大小（字节）
MAX_AUDIO_SIZE=52428800   # 50MB

# 上传临时目录
UPLOAD_DIR=./uploads
```

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | ✅ | - | PostgreSQL 连接字符串 |
| `SECRET_KEY` | ✅ | - | JWT 签名密钥，必须保密 |
| `AVATAR_SERVICE_URL` | ✅ | `http://localhost:8001` | Avatar Service 地址 |
| `FRONTEND_URL` | ❌ | - | CORS 白名单 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `10080` | Token 过期时间（7天） |
| `DEBUG` | ❌ | `false` | 调试模式 |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |

---

## 🤖 Avatar Service 配置

### 文件：`avatar_service/.env`

```bash
# =============================================================================
# LLM 配置（Ollama）
# =============================================================================

# Ollama API 地址
OLLAMA_BASE_URL=http://localhost:11434

# Docker 容器内访问宿主机
# OLLAMA_BASE_URL=http://host.docker.internal:11434

# 远程 Ollama 服务
# OLLAMA_BASE_URL=http://192.168.1.100:11434

# 默认 LLM 模型
DEFAULT_LLM_MODEL=mistral-nemo:12b

# 备用模型
FALLBACK_LLM_MODEL=llama3.1:8b

# =============================================================================
# 内部服务配置
# =============================================================================

# Lip-Sync Service URL（Avatar 生成和 WebRTC）
LIPSYNC_SERVICE_URL=http://localhost:8615

# Docker Compose 内使用服务名
# LIPSYNC_SERVICE_URL=http://lip-sync:8615

# TTS Service URL（语音合成）
TTS_SERVICE_URL=http://localhost:8604

# Docker Compose 内使用服务名
# TTS_SERVICE_URL=http://tts:8604

# =============================================================================
# Avatar 配置
# =============================================================================

# 默认 Avatar 模型
DEFAULT_AVATAR_MODEL=MuseTalk

# 支持的模型：MuseTalk, wav2lip, ultralight
AVATAR_MODELS=MuseTalk,wav2lip,ultralight

# 默认 TTS 模型
DEFAULT_TTS_MODEL=edge-tts

# 支持的 TTS 引擎：edge-tts, cosyvoice, sovits
TTS_MODELS=edge-tts,cosyvoice,sovits

# =============================================================================
# 超时配置（秒）
# =============================================================================

# Avatar 创建超时（2-10 分钟，取决于硬件）
AVATAR_CREATE_TIMEOUT=600

# Avatar 启动超时（1-5 分钟）
AVATAR_START_TIMEOUT=300

# 一般操作超时
AVATAR_OPERATION_TIMEOUT=30

# LLM 推理超时
LLM_TIMEOUT=60

# TTS 合成超时
TTS_TIMEOUT=30

# =============================================================================
# 文件路径配置
# =============================================================================

# Avatar 数据目录
AVATAR_DATA_DIR=./data/avatars

# TTS 缓存目录
TTS_CACHE_DIR=./data/tts_cache

# 模型存储目录
MODEL_DIR=./models

# =============================================================================
# 性能配置
# =============================================================================

# LLM 最大 token 数
MAX_TOKENS=2048

# LLM 温度（0.0-1.0）
TEMPERATURE=0.7

# 流式输出
STREAM_RESPONSE=true
```

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `OLLAMA_BASE_URL` | ✅ | `http://localhost:11434` | Ollama API 地址 |
| `LIPSYNC_SERVICE_URL` | ✅ | `http://localhost:8615` | Lip-Sync 服务地址 |
| `TTS_SERVICE_URL` | ✅ | `http://localhost:8604` | TTS 服务地址 |
| `DEFAULT_LLM_MODEL` | ❌ | `mistral-nemo:12b` | 默认 LLM 模型 |
| `DEFAULT_AVATAR_MODEL` | ❌ | `MuseTalk` | 默认 Avatar 模型 |
| `DEFAULT_TTS_MODEL` | ❌ | `edge-tts` | 默认 TTS 引擎 |
| `AVATAR_CREATE_TIMEOUT` | ❌ | `600` | Avatar 创建超时 |

---

## 🎨 Frontend 配置

### 文件：`frontend/.env.local`

```bash
# =============================================================================
# API 配置
# =============================================================================

# Web Backend API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000

# 生产环境
# NEXT_PUBLIC_API_URL=https://api.your-domain.com

# =============================================================================
# Avatar Frontend 配置
# =============================================================================

# Avatar Frontend 地址（用于显示给 Admin）
NEXT_PUBLIC_AVATAR_FRONTEND_URL=http://localhost:8080

# 生产环境
# NEXT_PUBLIC_AVATAR_FRONTEND_URL=https://avatar.your-domain.com
```

### Avatar Frontend 配置

**文件**：`avatar_frontend/app.js` (修改 CONFIG 对象)

```javascript
const CONFIG = {
    // Web Backend URL
    WEB_BACKEND_URL: 'http://localhost:8000',
    
    // Avatar Service URL (直连)
    AVATAR_SERVICE_URL: 'http://localhost:8001',
    
    // Tutor ID（从 URL 参数获取）
    TUTOR_ID: new URLSearchParams(window.location.search).get('tutor_id') || '1'
};
```

---

## 🔌 内部服务配置

### Lip-Sync Service

**文件**：`services/lip-sync/lip-sync.json`

```json
{
  "port": 8615,
  "host": "0.0.0.0",
  
  "models": {
    "musetalk": {
      "model_path": "./models/musetalk",
      "checkpoint": "pytorch_model.pth"
    },
    "wav2lip": {
      "model_path": "./models/wav2lip",
      "checkpoint": "wav2lip.pth"
    },
    "ultralight": {
      "model_path": "./models/ultralight",
      "checkpoint": "checkpoint.pth"
    }
  },
  
  "gpu": {
    "enabled": true,
    "device": "cuda:0"
  },
  
  "data": {
    "avatar_dir": "./data/avatars",
    "temp_dir": "./data/temp"
  }
}
```

### TTS Service

**文件**：`services/tts/config.json` (可选)

```json
{
  "port": 8604,
  "host": "0.0.0.0",
  
  "engines": {
    "edge-tts": {
      "enabled": true,
      "default_voice": "zh-CN-XiaoxiaoNeural"
    },
    "cosyvoice": {
      "enabled": true,
      "model_path": "./models/cosyvoice"
    },
    "sovits": {
      "enabled": true,
      "model_path": "./models/sovits"
    }
  },
  
  "cache": {
    "enabled": true,
    "dir": "./cache",
    "max_size_mb": 1024
  }
}
```

---

## 🐳 Docker 配置

### Docker Compose

**文件**：`docker-compose.yml`

```yaml
version: '3.8'

services:
  # =============================================================================
  # Avatar Service (AI 推理引擎)
  # =============================================================================
  avatar-service:
    build: ./avatar_service
    container_name: vtutor-avatar-service
    ports:
      - "8001:8001"
    environment:
      # LLM
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - DEFAULT_LLM_MODEL=mistral-nemo:12b
      
      # Internal Services (Docker 内部)
      - LIPSYNC_SERVICE_URL=http://lip-sync:8615
      - TTS_SERVICE_URL=http://tts:8604
      
      # Timeouts
      - AVATAR_CREATE_TIMEOUT=600
      - AVATAR_START_TIMEOUT=300
    depends_on:
      - lip-sync
      - tts
    networks:
      - vtutor-network
    restart: unless-stopped

  # =============================================================================
  # Lip-Sync Service (Avatar 生成 + WebRTC)
  # =============================================================================
  lip-sync:
    build: ./services/lip-sync
    container_name: vtutor-lip-sync
    ports:
      - "8615:8615"
    volumes:
      - ./data/avatars:/app/data/avatars
      - ./models:/app/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - vtutor-network
    restart: unless-stopped

  # =============================================================================
  # TTS Service (语音合成)
  # =============================================================================
  tts:
    build: ./services/tts
    container_name: vtutor-tts
    ports:
      - "8604:8604"
    volumes:
      - ./data/tts_cache:/app/cache
      - ./models/tts:/app/models
    networks:
      - vtutor-network
    restart: unless-stopped

networks:
  vtutor-network:
    driver: bridge

volumes:
  avatar-data:
  tts-cache:
```

### Dockerfile 示例

**Avatar Service**：
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## 🔐 安全配置

### 1. SECRET_KEY 生成

```bash
# 方法 1: Python
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 方法 2: OpenSSL
openssl rand -base64 64

# 方法 3: uuidgen
uuidgen | sha256sum | base64
```

### 2. 数据库安全

```bash
# 修改默认密码
ALTER USER vtutor_user WITH PASSWORD 'new_secure_password';

# 限制远程连接
# 编辑 /etc/postgresql/15/main/pg_hba.conf
host    virtual_tutor    vtutor_user    127.0.0.1/32    md5
```

### 3. HTTPS 配置

生产环境必须使用 HTTPS：

```nginx
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 监控配置

### 日志配置

**Web Backend**：
```python
# app_backend/app/core/logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### 健康检查

所有服务都提供 `/health` 端点：

```bash
# Web Backend
curl http://localhost:8000/health

# Avatar Service
curl http://localhost:8001/health

# Lip-Sync Service
curl http://localhost:8615/health

# TTS Service
curl http://localhost:8604/health
```

---

## 🚀 部署检查清单

### 开发环境
- [ ] PostgreSQL 安装并运行
- [ ] Ollama 安装并拉取模型
- [ ] Python 虚拟环境创建
- [ ] 所有 `.env` 文件创建
- [ ] 数据库迁移完成
- [ ] 创建测试 Admin 账号

### 生产环境
- [ ] 修改所有默认密码
- [ ] 生成新的 SECRET_KEY
- [ ] 配置 HTTPS
- [ ] 设置防火墙规则
- [ ] 配置日志收集
- [ ] 设置自动备份
- [ ] 配置监控告警
- [ ] 测试灾难恢复流程

---

## 🔧 常见配置问题

### 1. 无法连接 Ollama

**问题**：Avatar Service 无法连接 Ollama

**解决**：
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# Docker 容器内访问宿主机
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 2. Avatar 创建超时

**问题**：Avatar 创建时间过长

**解决**：
```bash
# 增加超时时间
AVATAR_CREATE_TIMEOUT=1200  # 20 分钟

# 或使用更快的 GPU
# 或减小视频分辨率
```

### 3. CORS 错误

**问题**：Frontend 无法访问 API

**解决**：
```bash
# 添加前端地址到 CORS 白名单
FRONTEND_URL=http://localhost:3000,http://localhost:8080,http://192.168.1.100:3000
```

---

## 📚 相关文档

- [README.md](README.md) - 项目介绍
- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
- [CLAUDE.md](CLAUDE.md) - 开发日志
- [API_VERIFICATION.md](API_VERIFICATION.md) - API 验证报告

---

**最后更新**：2025-12-18
