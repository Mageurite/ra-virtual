# Virtual Tutor 系统完整部署指南

## 📋 系统架构

Virtual Tutor 采用微服务架构，包含两个独立服务：

```
┌─────────────────────────────────────┐
│  Avatar Frontend (Browser)          │
│  - 视频对话界面                     │
│  - WebRTC 连接                      │
│  - 文字聊天                         │
│  Port: 8080 (配置)                  │
└─────────────────────────────────────┘
              ↓ HTTP
┌─────────────────────────────────────┐
│  Web Backend (Server A)             │
│  - 认证授权 (JWT)                   │
│  - 数据库管理 (PostgreSQL)          │
│  - Admin/Tutor/Student 管理         │
│  - 代理到 Avatar Service            │
│  Port: 8000 (配置)                  │
└─────────────────────────────────────┘
              ↓ HTTP (环境变量)
┌─────────────────────────────────────┐
│  Avatar Service (Serverless AI)     │
│  - LLM 推理 (Ollama)                │
│  - Avatar 管理                      │
│  - TTS 语音合成                     │
│  - 完全无状态                       │
│  Port: 8001 (配置)                  │
└─────────────────────────────────────┘
       ↓ HTTP (环境变量)
┌─────────────────────────────────────┐
│  Internal Services (项目内)         │
│  - Lip-Sync Service (8615)          │
│    位置: services/lip-sync/         │
│  - TTS Service (8604)               │
│    位置: services/tts/              │
└─────────────────────────────────────┘
       ↓ HTTP (环境变量)
┌─────────────────────────────────────┐
│  Third-Party Dependencies           │
│  - Ollama (11434)                   │
│  - PostgreSQL (5432)                │
└─────────────────────────────────────┘

所有服务地址通过环境变量配置，无硬编码。
```

---

## 🔧 环境要求

### 硬件要求
- **CPU**: 4 核以上
- **内存**: 16GB+ (推荐 32GB)
- **存储**: 50GB+ (用于模型和数据)
- **GPU**: 可选 (用于加速 LLM 推理)

### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+) / macOS
- **Python**: 3.10+
- **Node.js**: 18+ (前端)
- **PostgreSQL**: 15+
- **Docker**: 可选 (推荐用于生产环境)

---

## 🚀 快速开始 (开发环境)

### 步骤 1: 安装 PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@15

# 启动 PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS

# 创建数据库
sudo -u postgres psql
CREATE DATABASE virtual_tutor;
CREATE USER vtutor_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE virtual_tutor TO vtutor_user;
\q
```

### 步骤 2: 安装 Ollama
```bash
# 方法 1: 官方安装脚本
curl -fsSL https://ollama.ai/install.sh | sh

# 方法 2: 手动下载
# 访问 https://ollama.ai/download

# 启动 Ollama
ollama serve

# 下载模型
ollama pull mistral-nemo:12b-instruct-2407-fp16
# 或轻量级模型
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 步骤 2.5: 部署内部服务（Lip-Sync 和 TTS）

**项目包含**: 这些服务已包含在 `services/` 目录中。

#### 安装 Lip-Sync 服务

```bash
cd services/lip-sync

# 安装依赖
pip install -r requirements.txt

# 下载模型文件（根据需要）
# 模型文件放在 models/ 目录
# 具体模型链接请参考 services/lip-sync/README.md

# 配置（可选，使用环境变量）
export MODEL_PATH=/path/to/models  # 可选，默认使用 ./models
export GPU_DEVICE=0  # 指定 GPU 设备

# 启动服务（端口通过参数指定）
python live_server.py --port 8615
```

#### 安装 TTS 服务

```bash
cd services/tts

# 安装依赖
pip install -r requirements.txt

# 下载模型文件（根据需要）
# 模型文件放在各引擎目录下（edge/, cosyvoice/, sovits/）
# 具体模型链接请参考 services/tts/README.md

# 配置（可选，使用环境变量）
export TTS_MODEL_PATH=/path/to/models  # 可选
export TTS_CACHE_DIR=/path/to/cache    # 可选

# 启动服务（端口通过参数指定）
python tts.py --port 8604
```

#### 服务功能

**Lip-Sync 服务**:
- Avatar 视频生成和实时渲染
- WebRTC 支持，低延迟视频传输
- 嘴型同步（音频驱动面部动画）
- 支持多种 Avatar 模型（MuseTalk, Wav2Lip, UltraLight）

**TTS 服务**:
- Edge-TTS: 微软在线语音合成（免费）
- CosyVoice: 本地高质量 TTS
- GPT-SoVITS: 语音克隆和个性化合成
- Tacotron2: 经典 TTS 模型

#### 验证服务

```bash
# 检查 Lip-Sync 服务
curl http://localhost:8615/health

# 检查 TTS 服务  
curl http://localhost:8604/health

# 列出可用 Avatars
curl http://localhost:8615/avatar/get_avatars
```

#### 配置 Avatar Service 连接

在 `avatar_service/.env` 中配置服务地址（使用环境变量，无硬编码）:

```bash
# Lip-Sync 服务地址（可根据部署环境修改）
LIPSYNC_SERVICE_URL=http://localhost:8615

# TTS 服务地址（可根据部署环境修改）
TTS_SERVICE_URL=http://localhost:8604
```

**部署灵活性**:
- 本地开发: `http://localhost:8615`
- Docker: `http://lipsync:8615`
- 远程: `http://192.168.1.100:8615` 或域名

### 步骤 3: 部署 Web Backend
```bash
cd virtual_tutor/app_backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

编辑 `.env`:
```bash
DATABASE_URL=postgresql://vtutor_user:your_password@localhost:5432/virtual_tutor
SECRET_KEY=your-secret-key-change-in-production-use-random-string
AVATAR_SERVICE_URL=http://localhost:8001
```

```bash
# 运行数据库迁移（自动创建表）
# 或手动启动一次，FastAPI 会自动创建表
uvicorn app.main:app --reload --port 8000
```

### 步骤 4: 部署 Avatar Frontend
```bash
cd virtual_tutor/avatar_frontend

# 启动 HTTP 服务器（开发环境）
python3 -m http.server 8080

# 或使用 Node.js
npx http-server -p 8080
```

**配置说明**（`app.js`）:
```javascript
const CONFIG = {
    WEB_BACKEND_URL: 'http://localhost:8000',
    AVATAR_SERVICE_URL: 'http://localhost:8001',
    TUTOR_ID: '1'  // 从 URL 参数获取
};
```

**访问地址**:
- 默认访问: http://localhost:8080
- 指定导师: http://localhost:8080?tutor_id=1

**生产环境**: 使用 Nginx 或 Apache 托管静态文件。

---

### 步骤 5: 部署 Avatar Service
```bash
cd virtual_tutor/avatar_service

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env
```

编辑 `.env`:
```bash
OLLAMA_BASE_URL=http://localhost:11434
LLM_DEFAULT_MODEL=mistral-nemo:12b-instruct-2407-fp16

# 如果需要 Avatar 功能，配置 Mageurite
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604
```

```bash
# 启动服务
uvicorn main:app --reload --port 8001
```

### 步骤 6: 验证部署
```bash
# 检查 Web Backend
curl http://localhost:8000/health

# 检查 Avatar Service
curl http://localhost:8001/health

# 检查 LLM
curl -X POST http://localhost:8001/api/chat/completion \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# 检查 Avatar 功能（需要先启动 Mageurite）
curl http://localhost:8001/api/avatar/health

# 检查 TTS 功能
curl http://localhost:8001/api/tts/health

# 访问 API 文档
open http://localhost:8000/docs
open http://localhost:8001/docs

# 检查前端
curl http://localhost:8080
open http://localhost:8080
```

---

## 🐳 Docker 部署 (生产环境)

### 完整 Docker Compose 配置

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: virtual_tutor
      POSTGRES_USER: vtutor_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vtutor_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Ollama LLM 服务
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Web Backend
  web-backend:
    build:
      context: ./app_backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://vtutor_user:${DB_PASSWORD}@db:5432/virtual_tutor
      - SECRET_KEY=${SECRET_KEY}
      - AVATAR_SERVICE_URL=http://avatar-service:8001
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "
        alembic upgrade head &&
        gunicorn app.main:app 
          --workers 4 
          --worker-class uvicorn.workers.UvicornWorker 
          --bind 0.0.0.0:8000
      "

  # Avatar Service (AI Engine)
  avatar-service:
    build:
      context: ./avatar_service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LLM_DEFAULT_MODEL=mistral-nemo:12b-instruct-2407-fp16
      - LIPSYNC_SERVICE_URL=http://lipsync:8615  # 环境变量配置
      - TTS_SERVICE_URL=http://tts:8604  # 环境变量配置
    depends_on:
      - ollama
      - lipsync
      - tts
    command: >
      gunicorn main:app 
        --workers 4 
        --worker-class uvicorn.workers.UvicornWorker 
        --bind 0.0.0.0:8001 
        --timeout 300

  # Avatar Frontend
  frontend:
    image: nginx:alpine
    volumes:
      - ./avatar_frontend:/usr/share/nginx/html:ro
    ports:
      - "8080:80"
    depends_on:
      - web-backend
      - avatar-service

  # Lip-Sync Service (内部服务)
  lipsync:
    build:
      context: ./services/lip-sync
      dockerfile: Dockerfile
    ports:
      - "8615:8615"
    volumes:
      - ./services/lip-sync/models:/app/models:ro
      - ./services/lip-sync/data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
      - MODEL_PATH=/app/models  # 可配置
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: python live_server.py --port 8615

  # TTS Service (内部服务)
  tts:
    build:
      context: ./services/tts
      dockerfile: Dockerfile
    ports:
      - "8604:8604"
    volumes:
      - ./services/tts/models:/app/models:ro
      - tts-cache:/tmp/tts_cache
    environment:
      - PYTHONUNBUFFERED=1
      - TTS_MODEL_PATH=/app/models  # 可配置
      - TTS_CACHE_DIR=/tmp/tts_cache  # 可配置
    command: python tts.py --port 8604

volumes:
  postgres-data:
  ollama-data:
  tts-cache:
```

创建 `.env` 文件:
```bash
DB_PASSWORD=your_secure_password
SECRET_KEY=your_jwt_secret_key_min_32_chars
```

启动所有服务:
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 🔥 生产环境优化

### 1. 使用 Nginx 作为反向代理

`/etc/nginx/sites-available/virtual-tutor`:
```nginx
upstream web_backend {
    server localhost:8000;
}

upstream avatar_service {
    server localhost:8001;
}

# Web Backend (公开访问)
server {
    listen 80;
    server_name tutor.yourdomain.com;

    location / {
        proxy_pass http://web_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://web_backend/docs;
    }

    # WebSocket 支持
    location /ws {
        proxy_pass http://web_backend/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Avatar Service (内部访问 - 仅供 Web Backend)
server {
    listen 8001;
    server_name localhost;
    
    # 限制只能从本地访问
    allow 127.0.0.1;
    deny all;

    location / {
        proxy_pass http://avatar_service;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/virtual-tutor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL/TLS 配置 (Let's Encrypt)
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d tutor.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. Systemd 服务配置

**Web Backend** (`/etc/systemd/system/vtutor-web.service`):
```ini
[Unit]
Description=Virtual Tutor Web Backend
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/virtual_tutor/app_backend
Environment="PATH=/opt/virtual_tutor/app_backend/venv/bin"
Environment="DATABASE_URL=postgresql://..."
Environment="SECRET_KEY=..."
ExecStart=/opt/virtual_tutor/app_backend/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Avatar Service** (`/etc/systemd/system/vtutor-avatar.service`):
```ini
[Unit]
Description=Virtual Tutor Avatar Service
After=network.target vtutor-lipsync.service vtutor-tts.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/virtual_tutor/avatar_service
Environment="PATH=/opt/virtual_tutor/avatar_service/venv/bin"
Environment="OLLAMA_BASE_URL=http://localhost:11434"
Environment="LIPSYNC_SERVICE_URL=http://localhost:8615"
Environment="TTS_SERVICE_URL=http://localhost:8604"
ExecStart=/opt/virtual_tutor/avatar_service/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8001 \
  --timeout 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Lip-Sync Service** (`/etc/systemd/system/vtutor-lipsync.service`):
```ini
[Unit]
Description=Mageurite Lip-Sync Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mageurite/lip-sync
Environment="PATH=/opt/mageurite/lip-sync/venv/bin"
Environment="CUDA_VISIBLE_DEVICES=0"
ExecStart=/opt/mageurite/lip-sync/venv/bin/python live_server.py --port 8615
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**TTS Service** (`/etc/systemd/system/vtutor-tts.service`):
```ini
[Unit]
Description=Mageurite TTS Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mageurite/tts
Environment="PATH=/opt/mageurite/tts/venv/bin"
ExecStart=/opt/mageurite/tts/venv/bin/python app.py --port 8604
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用所有服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vtutor-web vtutor-avatar vtutor-lipsync vtutor-tts
sudo systemctl start vtutor-web vtutor-avatar vtutor-lipsync vtutor-tts
sudo systemctl status vtutor-web vtutor-avatar vtutor-lipsync vtutor-tts
```

---

## 📊 监控和日志

### 健康检查脚本
创建 `monitor.sh`:
```bash
#!/bin/bash

ENDPOINTS=(
    "http://localhost:8000/health|Web Backend"
    "http://localhost:8001/health|Avatar Service"
    "http://localhost:8080|Frontend"
    "http://localhost:11434/api/tags|Ollama"
    "http://localhost:8615/health|Lip-Sync Service"
    "http://localhost:8604/health|TTS Service"
)

for endpoint in "${ENDPOINTS[@]}"; do
    IFS='|' read -r url name <<< "$endpoint"
    if curl -sf "$url" > /dev/null 2>&1; then
        echo "✅ $name: OK"
    else
        echo "❌ $name: DOWN"
        # 发送告警（例如: 邮件、Slack、钉钉）
    fi
done
```

定时检查 (crontab):
```bash
# 每 5 分钟检查一次
*/5 * * * * /opt/virtual_tutor/monitor.sh
```

### 日志聚合
```bash
# 使用 journalctl 查看服务日志
journalctl -u vtutor-web -f
journalctl -u vtutor-avatar -f

# 或配置文件日志
tail -f /var/log/vtutor/web.log
tail -f /var/log/vtutor/avatar.log
```

---

## 🐛 常见问题

### Q1: PostgreSQL 连接失败
```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查连接字符串
psql "postgresql://vtutor_user:password@localhost:5432/virtual_tutor"
```

### Q2: Ollama 响应慢
```bash
# 使用更小的模型
ollama pull llama3.1:8b

# 或启用 GPU 加速
# 确保安装了 NVIDIA 驱动和 CUDA
```

### Q3: Lip-Sync 服务启动失败
```bash
# 检查 GPU 驱动
nvidia-smi

# 检查 CUDA 是否可用
python -c "import torch; print(torch.cuda.is_available())"

# 检查模型文件是否存在
ls -lh /opt/mageurite/lip-sync/models/

# 检查日志
journalctl -u vtutor-lipsync -n 50

# 手动测试启动
cd /opt/mageurite/lip-sync
source venv/bin/activate
python live_server.py --port 8615
```

### Q4: Avatar Service 无法连接到 Lip-Sync
```bash
# 检查 Lip-Sync 服务状态
curl http://localhost:8615/health
systemctl status vtutor-lipsync

# 检查防火墙
sudo ufw allow 8000
sudo ufw allow 8001
sudo ufw allow 8615
sudo ufw allow 8604

# 检查服务监听
netstat -tlnp | grep 8615
netstat -tlnp | grep 8604
```

### Q5: 前端无法访问 API
```bash
# 检查 CORS 配置
# 在 app_backend/app/main.py 中确认 CORS 设置

# 检查前端配置
# 在 avatar_frontend/app.js 中确认 API URL
```

### Q6: WebRTC 连接失败
```bash
# 检查浏览器权限（麦克风）
# 检查 Mageurite Lip-Sync 服务
curl http://localhost:8615/health
systemctl status vtutor-lipsync

# 检查 STUN 服务器可访问性
# 在浏览器控制台查看 WebRTC 错误

# 测试 Avatar 创建
curl -X POST http://localhost:8615/api/avatar/create \
  -H "Content-Type: application/json" \
  -d '{"avatar_id": "test"}'
```

### Q7: TTS 语音合成失败
```bash
# 检查 TTS 服务
curl http://localhost:8604/health
systemctl status vtutor-tts

# 检查 Avatar Service TTS 配置
curl http://localhost:8001/api/tts/health

# 测试语音合成
curl -X POST http://localhost:8604/synthesize \
  -F "text=你好" \
  -F "engine=edge-tts" \
  -F "voice=zh-CN-XiaoxiaoNeural"
```

### Q8: Avatar 视频无画面
```bash
# 检查完整调用链
curl http://localhost:8001/api/avatar/health  # Avatar Service
curl http://localhost:8615/health              # Lip-Sync
curl http://localhost:8604/health              # TTS

# 检查 Avatar 状态
curl http://localhost:8001/api/avatar/list

# 查看详细日志
journalctl -u vtutor-avatar -f
journalctl -u vtutor-lipsync -f

# 检查模型文件完整性
md5sum /opt/mageurite/lip-sync/models/*.pth
```

---

## 📚 相关文档

- [Web Backend README](app_backend/README.md)
- [Avatar Service README](avatar_service/README.md)
- [Avatar Service Deployment](avatar_service/DEPLOYMENT.md)
- [Avatar Frontend README](avatar_frontend/README.md)
- [Architecture Overview](ARCHITECTURE.md)

---

## 📈 性能基准

**硬件**: 8核CPU, 32GB RAM, NVIDIA RTX 3090

| 服务 | QPS | 平均延迟 | P99 延迟 |
|------|-----|----------|----------|
| Web Backend (CRUD) | 1000+ | 20ms | 50ms |
| LLM Completion | 10 | 2s | 5s |
| LLM Streaming | 20 | 500ms | 1s |
| Avatar Creation | - | 30s | 60s |

---

## 🔒 安全建议

1. **修改默认密码**: 更改所有 `.env` 中的密码
2. **限制网络访问**: Avatar Service 仅允许 Web Backend 访问
3. **启用 HTTPS**: 生产环境必须使用 SSL/TLS
4. **定期更新**: 保持依赖包最新版本
5. **备份数据库**: 定期备份 PostgreSQL 数据

---

## 💬 技术支持

- GitHub Issues
- 文档: http://localhost:8000/docs
- 邮件支持: support@yourdomain.com

---

**版本**: v1.0.0  
**更新时间**: 2025-12-18
