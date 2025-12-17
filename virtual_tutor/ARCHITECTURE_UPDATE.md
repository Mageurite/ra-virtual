# Virtual Tutor - 自包含架构

## ✅ 架构更新

Virtual Tutor 现在是**完全自包含**的项目，所有服务都在项目内部，无外部依赖。

---

## 📦 项目结构

```
virtual_tutor/
├── app_backend/          # Web Backend (端口可配置)
├── avatar_service/       # Avatar AI Engine (端口可配置)
├── avatar_frontend/      # 前端界面 (端口可配置)
└── services/             # 内部服务
    ├── lip-sync/         # Avatar 视频服务
    └── tts/              # 语音合成服务
```

**所有服务都在项目内，无需外部依赖。**

---

## 🔧 配置原则

### ✅ 零硬编码

所有路径、端口、URL 都通过以下方式配置：

1. **环境变量** (推荐)
   ```bash
   # avatar_service/.env
   LIPSYNC_SERVICE_URL=http://localhost:8615
   TTS_SERVICE_URL=http://localhost:8604
   ```

2. **命令行参数**
   ```bash
   python live_server.py --port 8615
   python tts.py --port 8604
   ```

3. **配置文件**
   ```json
   {
     "lipsync_url": "http://localhost:8615",
     "tts_url": "http://localhost:8604"
   }
   ```

**绝不使用硬编码路径或 URL。**

---

## 🚀 部署灵活性

### 本地开发

```bash
# 使用 localhost
export LIPSYNC_SERVICE_URL=http://localhost:8615
export TTS_SERVICE_URL=http://localhost:8604
```

### Docker Compose

```yaml
# 使用服务名称
environment:
  - LIPSYNC_SERVICE_URL=http://lipsync:8615
  - TTS_SERVICE_URL=http://tts:8604
```

### 远程部署

```bash
# 使用 IP 或域名
export LIPSYNC_SERVICE_URL=http://192.168.1.100:8615
export TTS_SERVICE_URL=http://192.168.1.200:8604
```

---

## 📋 服务清单

| 服务 | 默认端口 | 配置方式 | 位置 |
|------|---------|---------|------|
| Web Backend | 8000 | 环境变量 | `app_backend/` |
| Avatar Service | 8001 | 环境变量 | `avatar_service/` |
| Frontend | 8080 | 静态托管 | `avatar_frontend/` |
| Lip-Sync | 8615 | 环境变量/参数 | `services/lip-sync/` |
| TTS | 8604 | 环境变量/参数 | `services/tts/` |

**所有端口都可以通过配置修改。**

---

## 🔌 服务连接

### Web Backend → Avatar Service

```python
# app_backend/app/main.py (无硬编码)
AVATAR_SERVICE_URL = os.getenv("AVATAR_SERVICE_URL", "http://localhost:8001")
```

### Avatar Service → Internal Services

```python
# avatar_service/avatar/config.py (无硬编码)
LIPSYNC_SERVICE_URL = os.getenv("LIPSYNC_SERVICE_URL", "http://localhost:8615")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:8604")
```

### Frontend → Web Backend

```javascript
// avatar_frontend/app.js (无硬编码)
const CONFIG = {
    WEB_BACKEND_URL: 'http://localhost:8000',  // 可通过构建时注入修改
    AVATAR_SERVICE_URL: 'http://localhost:8001'
};
```

---

## 🎯 配置示例

### .env 文件示例

**app_backend/.env**:
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/vtutor
SECRET_KEY=your-secret-key
AVATAR_SERVICE_URL=http://localhost:8001
```

**avatar_service/.env**:
```bash
OLLAMA_BASE_URL=http://localhost:11434
LLM_DEFAULT_MODEL=mistral-nemo:12b
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604
```

**services/lip-sync/.env** (可选):
```bash
MODEL_PATH=/path/to/models
GPU_DEVICE=0
PORT=8615
```

**services/tts/.env** (可选):
```bash
TTS_MODEL_PATH=/path/to/models
TTS_CACHE_DIR=/tmp/tts_cache
PORT=8604
```

---

## ✅ 验证检查

确认系统无硬编码：

```bash
# 搜索硬编码 URL（应该没有结果）
grep -r "http://localhost:8615" app_backend/ avatar_service/ --exclude-dir=.git

# 搜索硬编码路径（应该只在 .env.example 中）
grep -r "LIPSYNC_SERVICE_URL" app_backend/ avatar_service/

# 确认都使用 os.getenv()
grep -r "os.getenv" app_backend/ avatar_service/
```

---

## 📚 相关文档

- [系统部署指南](DEPLOYMENT.md) - 完整部署流程
- [系统状态报告](SYSTEM_STATUS.md) - 实现完整性
- [服务说明](services/README.md) - 内部服务文档
- [测试连接](avatar_frontend/TEST_CONNECTION.md) - 连接测试

---

## 🎉 优势

1. ✅ **自包含** - 所有服务在项目内
2. ✅ **零硬编码** - 全部通过配置
3. ✅ **灵活部署** - 本地/Docker/远程都可以
4. ✅ **易于维护** - 统一管理所有服务
5. ✅ **便于扩展** - 添加新服务只需配置

---

**版本**: v1.0.0  
**更新时间**: 2025-12-18
