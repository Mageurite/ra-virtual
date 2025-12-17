# Avatar Service 部署指南

## 📋 概述

Avatar Service 是 Virtual Tutor 系统的 AI 推理引擎，提供：
- **LLM 对话服务** (Ollama)
- **Avatar 管理服务** (Mageurite 集成)
- **WebRTC 实时通信代理**

本服务完全无状态，无需数据库，可独立部署和扩展。

---

## 🔧 环境要求

### 系统要求
- **操作系统**: Linux / macOS / Windows
- **Python**: 3.10+ 
- **内存**: 最低 8GB (推荐 16GB+)
- **GPU**: 可选 (推荐用于 Ollama LLM 推理)

### 依赖服务
1. **Ollama** (LLM 推理引擎) - 必需
   - 下载: https://ollama.ai/download
   - 端口: `11434` (默认)

2. **Mageurite Lip-Sync Service** (Avatar 生成) - 可选
   - 端口: `8615` (默认)
   - 仓库: mageurite_virtual_tutor/lip-sync

3. **Mageurite TTS Service** (语音合成) - 可选
   - 端口: `8604` (默认)
   - 仓库: mageurite_virtual_tutor/tts

---

## 🚀 快速部署

### 1. 克隆代码
```bash
cd virtual_tutor/avatar_service
```

### 2. 创建 Python 虚拟环境 (推荐)
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env
```

**必需配置**:
```bash
# Ollama 服务地址
OLLAMA_BASE_URL=http://localhost:11434

# LLM 模型（确保已下载）
LLM_DEFAULT_MODEL=mistral-nemo:12b-instruct-2407-fp16

# 服务端口
PORT=8001
```

**可选配置** (如果使用 Avatar 功能):
```bash
# Mageurite 服务地址
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604
```

### 5. 下载 LLM 模型
```bash
# 确保 Ollama 正在运行
ollama serve &

# 下载模型（首次使用）
ollama pull mistral-nemo:12b-instruct-2407-fp16

# 或使用更轻量的模型
ollama pull llama3.1:8b-instruct-q4_K_M
```

### 6. 启动服务
```bash
# 开发模式（自动重载）
uvicorn main:app --reload --port 8001

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### 7. 验证部署
```bash
# 健康检查
curl http://localhost:8001/health

# 测试 LLM
curl -X POST http://localhost:8001/api/chat/completion \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# 查看 API 文档
open http://localhost:8001/docs
```

---

## 🐳 Docker 部署

### 使用 Dockerfile
```bash
# 构建镜像
docker build -t avatar-service:latest .

# 运行容器
docker run -d \
  --name avatar-service \
  -p 8001:8001 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  avatar-service:latest
```

### 使用 Docker Compose
创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  avatar-service:
    build: .
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - LIPSYNC_SERVICE_URL=http://mageurite-lipsync:8615
      - TTS_SERVICE_URL=http://mageurite-tts:8604
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

volumes:
  ollama-data:
```

启动:
```bash
docker-compose up -d
```

---

## 🔥 生产部署

### 使用 Gunicorn (推荐)
```bash
# 安装 Gunicorn
pip install gunicorn uvicorn[standard]

# 启动服务
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

### 使用 Systemd 服务
创建 `/etc/systemd/system/avatar-service.service`:
```ini
[Unit]
Description=Avatar AI Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/virtual_tutor/avatar_service
Environment="PATH=/opt/virtual_tutor/avatar_service/venv/bin"
ExecStart=/opt/virtual_tutor/avatar_service/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable avatar-service
sudo systemctl start avatar-service
sudo systemctl status avatar-service
```

### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name avatar.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置（LLM 推理可能较慢）
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

---

## 📊 性能优化

### 1. 模型选择
根据硬件选择合适的 LLM 模型:

| 模型 | 参数量 | 内存需求 | 推理速度 | 质量 |
|------|--------|----------|----------|------|
| `llama3.1:8b-instruct-q4_K_M` | 8B | ~5GB | 快 | 良好 |
| `mistral-nemo:12b-instruct-2407-fp16` | 12B | ~25GB | 中等 | 优秀 |
| `llama3.1:70b` | 70B | ~40GB | 慢 | 极佳 |

### 2. Worker 数量
```bash
# CPU 密集型工作
workers = (CPU 核心数 × 2) + 1

# 示例：8 核 CPU
gunicorn main:app --workers 17
```

### 3. 缓存优化
在 `.env` 中配置:
```bash
# 启用模型预加载
OLLAMA_KEEP_ALIVE=24h

# 禁用不必要的功能
GUARDRAIL_ENABLED=false
RAG_ENABLED=false
```

---

## 🔍 健康监控

### API 端点
```bash
# 服务健康
GET /health

# LLM 健康
GET /api/chat/health

# Avatar 服务健康
GET /api/avatar/health
```

### 监控脚本
创建 `monitor.sh`:
```bash
#!/bin/bash
AVATAR_URL="http://localhost:8001"

# 检查服务
if curl -sf "$AVATAR_URL/health" > /dev/null; then
    echo "✅ Avatar Service: OK"
else
    echo "❌ Avatar Service: DOWN"
    # 发送告警...
fi

# 检查 Ollama
if curl -sf "http://localhost:11434/api/tags" > /dev/null; then
    echo "✅ Ollama: OK"
else
    echo "❌ Ollama: DOWN"
fi
```

---

## 🐛 故障排查

### 问题 1: 导入错误 `ModuleNotFoundError: No module named 'langchain_ollama'`
**解决方案**:
```bash
pip install -r requirements.txt
# 或单独安装
pip install langchain-ollama langchain-core
```

### 问题 2: Ollama 连接失败
**检查**:
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 启动 Ollama
ollama serve
```

### 问题 3: LLM 响应慢
**优化**:
```bash
# 使用更小的模型
ollama pull llama3.1:8b

# 或使用量化版本
ollama pull mistral-nemo:12b-q4_K_M
```

### 问题 4: 端口被占用
**解决**:
```bash
# 查看端口占用
lsof -i :8001

# 或更改端口
uvicorn main:app --port 8002
```

### 问题 5: Avatar Service 无法连接到 Mageurite
**检查**:
```bash
# 测试 Lip-Sync 服务
curl http://localhost:8615/avatar/get_avatars

# 测试 TTS 服务
curl http://localhost:8604/health
```

---

## 📈 扩展部署

### 水平扩展 (多实例)
```bash
# 实例 1
uvicorn main:app --port 8001 &

# 实例 2
uvicorn main:app --port 8002 &

# 实例 3
uvicorn main:app --port 8003 &
```

使用负载均衡器 (Nginx):
```nginx
upstream avatar_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location / {
        proxy_pass http://avatar_backend;
    }
}
```

### 垂直扩展 (GPU 加速)
```bash
# 配置 Ollama 使用 GPU
ollama serve

# 验证 GPU 使用
nvidia-smi
```

---

## 🔐 安全建议

1. **网络隔离**
   - Avatar Service 应该在内网运行
   - 仅允许 Web Backend 访问
   - 使用防火墙限制端口访问

2. **日志管理**
   ```bash
   # 配置日志轮转
   gunicorn main:app \
     --access-logfile /var/log/avatar/access.log \
     --error-logfile /var/log/avatar/error.log
   ```

3. **限流**
   ```python
   # 使用 slowapi 限流
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

---

## 📚 相关文档

- [README.md](README.md) - 服务介绍
- [Architecture Overview](../ARCHITECTURE.md) - 系统架构
- [API Documentation](http://localhost:8001/docs) - 接口文档
- [Ollama Documentation](https://ollama.ai/docs) - Ollama 官方文档

---

## 💬 支持

遇到问题？
1. 查看日志: `tail -f /var/log/avatar/error.log`
2. 检查健康状态: `curl http://localhost:8001/health`
3. 查看 API 文档: http://localhost:8001/docs
4. 提交 Issue: GitHub 项目仓库

---

## 📝 更新日志

- **v1.0.0** (2025-12-18)
  - 初始版本发布
  - LLM 对话服务
  - Avatar 管理集成
  - WebRTC 代理支持
