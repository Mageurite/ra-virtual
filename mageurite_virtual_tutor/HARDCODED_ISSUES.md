# 硬编码问题清单及修复指南

本文档列出了 Virtual Tutor 系统中所有需要修改的硬编码部分，以确保系统能够在不同环境中正常运行。

## 🚨 关键硬编码问题

### 1. **lip-sync/lip-sync.json** - 必须修改 ⚠️

**问题**：包含多个特定服务器的绝对路径

**当前内容**：
```json
{
  "paths": {
    "conda_init": "/workspace/conda/etc/profile.d/conda.sh",
    "conda_env": "/workspace/conda/envs/avatar",
    "muse_conda_env": "/workspace/conda/envs/MuseTalk",
    "ffmpeg_path": "/workspace/murphy/MuseTalk/ffmpeg-static/ffmpeg-7.0.2-amd64-static/ffmpeg",
    "working_directory": "/workspace/murphy/capstone-project-25t3-9900-virtual-tutor-phase-2/lip-sync",
    "muse_talk_base": "/workspace/murphy/MuseTalk"
  }
}
```

**修复方法**：
```json
{
  "paths": {
    "conda_init": "~/miniconda3/etc/profile.d/conda.sh",  // 或你的 conda 安装路径
    "conda_env": "nerfstream",  // 只需环境名，不需要完整路径
    "muse_conda_env": "MuseTalk",  // 只需环境名
    "ffmpeg_path": "ffmpeg",  // 使用系统 PATH 中的 ffmpeg
    "working_directory": "/absolute/path/to/your/lip-sync",  // 你的实际路径
    "muse_talk_base": "/absolute/path/to/your/MuseTalk"  // 如果使用外部 MuseTalk
  }
}
```

**获取路径的命令**：
```bash
# 获取 conda_init 路径
conda info | grep "base environment"
# 通常是 ~/miniconda3/etc/profile.d/conda.sh 或 ~/anaconda3/etc/profile.d/conda.sh

# 获取工作目录
pwd  # 在 lip-sync 目录下运行

# 检查 ffmpeg
which ffmpeg
```

---

### 2. **rag/app.py** - 临时目录硬编码 ⚠️

**问题**：
```python
TEMP_DIR = "/home/jialu/workspace/jialu/tmp"
```

**修复方法**：
```python
import tempfile
import os

# 选项 1: 使用系统临时目录（推荐）
TEMP_DIR = tempfile.gettempdir()

# 选项 2: 使用相对路径
TEMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(TEMP_DIR, exist_ok=True)

# 选项 3: 使用环境变量
TEMP_DIR = os.getenv("RAG_TEMP_DIR", os.path.join(os.path.dirname(__file__), "tmp"))
os.makedirs(TEMP_DIR, exist_ok=True)
```

**相同问题的文件**：
- `rag/chroma_db/app.py` (line 14)
- `rag/multimodal_kb/app.py` (line 26)
- `rag/milvus_kb/app.py` (line 15)

---

### 3. **rag/milvus_kb/config.py** - 模型路径硬编码 ⚠️

**问题**：
```python
MODEL_DIR = "/home/jialu/workspace/jialu/models/qwen3-embed-4b"
```

**修复方法**：
```python
import os

# 使用相对路径或环境变量
MODEL_DIR = os.getenv("EMBEDDING_MODEL_DIR", "./models/qwen3-embed-4b")
```

---

### 4. **rag/multimodal_kb/config.py** - 数据库和图片路径硬编码 ⚠️

**问题**：
```python
EMBEDDED_DB_PATH = "/home/jialu/workspace/jialu/capstone-project-25t2-9900-h16c-bread1/rag/multimodal_kb/KB/kb_test.db"
IMG_DIR = "/home/jialu/workspace/jialu/capstone-project-25t2-9900-h16c-bread1/rag/multimodal_kb/dataset/imgs"
```

**修复方法**：
```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDED_DB_PATH = os.getenv("EMBEDDED_DB_PATH", os.path.join(BASE_DIR, "KB", "kb_test.db"))
IMG_DIR = os.getenv("IMG_DIR", os.path.join(BASE_DIR, "dataset", "imgs"))

# 确保目录存在
os.makedirs(os.path.dirname(EMBEDDED_DB_PATH), exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)
```

---

### 5. **rag/chroma_db/config.py** - Chroma 数据库路径 ⚠️

**问题**：
```python
CHROMA_ROOT = os.getenv("CHROMA_ROOT", "/home/jialu/workspace/jialu/chroma_db")
```

**修复方法**：
```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_ROOT = os.getenv("CHROMA_ROOT", os.path.join(BASE_DIR, "chroma_db"))
os.makedirs(CHROMA_ROOT, exist_ok=True)
```

---

### 6. **lip-sync/app.py** - TTS 服务器地址 ⚠️

**问题**：
```python
parser.add_argument('--TTS_SERVER', type=str, default='http://127.0.0.1:9880')
```

**修复方法**：
应该使用配置文件中的值或环境变量：
```python
import os

default_tts_server = os.getenv('TTS_SERVER', 'http://127.0.0.1:8604')
parser.add_argument('--TTS_SERVER', type=str, default=default_tts_server)
```

---

### 7. **lip-sync/create_avatar.py** - Conda 路径硬编码 ⚠️

**问题**：
```python
conda_init = get_config_value("paths.conda_init", "/home/xinghua/workspace/share/conda/etc/profile.d/conda.sh")
conda_env = get_config_value("paths.muse_conda_env", "/workspace/share/yuntao/MuseTalk/home/chengxin/workspace/chengxin/conda/envs/MuseTalk")
```

**修复方法**：
这些应该从 lip-sync.json 配置文件读取，默认值应该更通用：
```python
conda_init = get_config_value("paths.conda_init", "~/miniconda3/etc/profile.d/conda.sh")
conda_env = get_config_value("paths.muse_conda_env", "MuseTalk")
```

---

## � 后端服务 URL 硬编码问题 ⚠️

### 11. **backend/routes/chat.py** - LLM 和 Lip-Sync 服务 URL

**问题**：后端调用其他服务时使用了硬编码的 localhost URL

```python
# Line 84
url="http://localhost:8610/chat/stream"

# Line 108, 122
requests.post("http://localhost:8615/human", json=forward_payload, timeout=10)

# Line 287
"http://localhost:8610/activate_model"
```

**修复方法**：
```python
import os

# 在文件开头定义
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8611")
LIPSYNC_SERVICE_URL = os.getenv("LIPSYNC_SERVICE_URL", "http://localhost:8615")

# 使用变量代替硬编码
url = f"{LLM_SERVICE_URL}/chat/stream"
requests.post(f"{LIPSYNC_SERVICE_URL}/human", json=forward_payload, timeout=10)
```

**注意**：端口 8610 应该是 8611（LLM 服务的正确端口）

---

### 12. **backend/routes/upload.py** - RAG 服务 URL

**问题**：多处硬编码 RAG 服务 URL

```python
# Lines 42, 44, 74, 77, 99, 116, 135
forward_url = "http://localhost:9090/user/upload"
forward_url = "http://localhost:9090/admin/upload"
forward_url = "http://localhost:9090/user/delete"
forward_url = "http://localhost:9090/admin/delete"
response = requests.get("http://localhost:9090/api/users", timeout=10)
"http://localhost:9090/api/user_files"
response = requests.get("http://localhost:9090/api/public_files", timeout=10)
```

**修复方法**：
```python
import os

RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8602")

# 使用变量
forward_url = f"{RAG_SERVICE_URL}/user/upload"
forward_url = f"{RAG_SERVICE_URL}/admin/upload"
# ... 其他类似
```

**注意**：端口 9090 应该是 8602（RAG 服务的正确端口）

---

### 13. **backend/routes/avatar.py** - Lip-Sync 和 TTS 服务 URL

**问题**：多处硬编码服务 URL

```python
# Line 13
webrtc_url = f"http://localhost:8615/{path}"

# Lines 41, 76, 123, 172, 203
"http://localhost:8606/avatar/get_avatars"
"http://localhost:8606/avatar/preview"
"http://localhost:8606/avatar/add"
"http://localhost:8606/avatar/delete"
"http://localhost:8606/avatar/start"

# Line 149
"http://localhost:8604/tts/models"
```

**修复方法**：
```python
import os

LIPSYNC_SERVICE_URL = os.getenv("LIPSYNC_SERVICE_URL", "http://localhost:8615")
TTS_SERVICE_URL = os.getenv("TTS_SERVICE_URL", "http://localhost:8604")

# 使用变量
webrtc_url = f"{LIPSYNC_SERVICE_URL}/{path}"
response = requests.get(f"{TTS_SERVICE_URL}/tts/models", timeout=10)
```

**注意**：端口 8606 应该改为 8615（或通过配置文件统一管理）

---

### 14. **backend/services/redis_client.py** - Redis 端口

**问题**：
```python
port=6379,  # Redis server port
```

**修复方法**：
```python
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)
```

---

### 15. **llm/milvus_config.py** - Milvus API URL

**问题**：
```python
MILVUS_API_BASE_URL: str = os.getenv("MILVUS_API_BASE_URL", "http://localhost:9090")
```

**修复方法**：端口应该是 8602，而不是 9090
```python
MILVUS_API_BASE_URL: str = os.getenv("MILVUS_API_BASE_URL", "http://localhost:8602")
```

---

### 16. **llm/milvus_api_client.py** - Milvus 客户端默认 URL

**问题**：
```python
self.base_url = (base_url or "http://localhost:9090").rstrip('/')
```

**修复方法**：
```python
self.base_url = (base_url or os.getenv("MILVUS_API_BASE_URL", "http://localhost:8602")).rstrip('/')
```

---

### 17. **rag/app.py** - 端口配置

**问题**：
```python
port=8602,  # 这个是对的
```

但其他 RAG 模块使用了不同端口：
- `rag/multimodal_kb/app.py`: port=9090
- `rag/milvus_kb/app.py`: port=9090
- `rag/chroma_db/app.py`: port=8080

**修复方法**：统一使用环境变量
```python
import os

PORT = int(os.getenv("RAG_SERVICE_PORT", "8602"))
app.run(host="0.0.0.0", port=PORT)
```

---

### 18. **tts/config.json** - TTS 端口配置

**当前内容**：
```json
{
    "tts_server_port": 8604
}
```

这个配置是正确的，但应该在代码中读取这个配置文件，而不是硬编码端口。

---

### 19. **lip-sync/live_server.py** - 端口硬编码

**问题**：
```python
# Line 512
uvicorn.run(app, host="0.0.0.0", port=8606)
```

**修复方法**：
```python
import os

PORT = int(os.getenv("LIPSYNC_SERVER_PORT", "8615"))
uvicorn.run(app, host="0.0.0.0", port=PORT)
```

**注意**：这个服务应该使用 8615，而不是 8606

---

## �📋 次要问题（测试文件）

以下是测试文件中的硬编码路径，不影响主系统运行，但在运行测试时需要修改：

### 8. **rag/milvus_kb/test_script.py**
```python
file_path = "/home/jialu/workspace/jialu/materials/Course Outline & Logistics.pdf"
```

### 9. **rag/chroma_db/test_script.py**
```python
path = "/home/jialu/workspace/jialu/materials"
file_path = "/home/jialu/workspace/jialu/materials/Course_Intro.pdf"
```

### 10. **rag/multimodal_kb/tests/conftest.py**
```python
TESTS_DIR = Path("/home/jialu/workspace/jialu/capstone-project-25t2-9900-h16c-bread1/rag/multimodal_kb/tests")
```

**修复方法**：使用相对路径
```python
import os
from pathlib import Path

# 获取当前文件所在目录
TESTS_DIR = Path(__file__).parent
```

---

## ✅ 已正确配置的部分

这些配置已经使用了相对路径或环境变量，**无需修改**：

### frontend/src/config.js ✅
动态获取 hostname，无硬编码问题：
```javascript
const config = {
    get BACKEND_URL() {
        const host = window.location.hostname;
        return `http://${host}:8203`;
    }
}
```

### backend/config.py ✅
使用环境变量和相对路径：
```python
BASEDIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'instance', 'app.db')
```

### rag/config.py ✅
使用相对路径：
```python
EMBEDDED_DB_PATH = "./kb_test.db"
IMG_DIR = "./imgs"
```

---

## 🛠️ 快速修复脚本

创建 `.env` 文件来配置环境变量（推荐方式）：

### backend/.env
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### rag/.env
```bash
RAG_TEMP_DIR=./tmp
EMBEDDING_MODEL_DIR=./models/qwen3-embed-4b
CHROMA_ROOT=./chroma_db
```

### lip-sync/.env
```bash
TTS_SERVER=http://127.0.0.1:8604
```

---

## 📝 修复检查清单

在运行系统之前，请确认以下检查项：

### 关键路径修复
- [ ] **lip-sync/lip-sync.json** - 所有路径已更新为你的实际路径
  - [ ] conda_init 路径正确
  - [ ] working_directory 路径正确
  - [ ] ffmpeg_path 可以访问（或使用系统 ffmpeg）

- [ ] **rag/app.py** - TEMP_DIR 已修改为相对路径或系统临时目录
- [ ] **rag/chroma_db/app.py** - TEMP_DIR 已修改
- [ ] **rag/multimodal_kb/app.py** - TEMP_DIR 已修改
- [ ] **rag/milvus_kb/app.py** - TEMP_DIR 已修改
- [ ] **rag/milvus_kb/config.py** - MODEL_DIR 已修改
- [ ] **rag/multimodal_kb/config.py** - EMBEDDED_DB_PATH 和 IMG_DIR 已修改
- [ ] **rag/chroma_db/config.py** - CHROMA_ROOT 已修改

### 服务 URL 修复
- [ ] **backend/routes/chat.py** - LLM 和 Lip-Sync URL 使用环境变量
- [ ] **backend/routes/upload.py** - RAG URL 使用环境变量（端口改为 8602）
- [ ] **backend/routes/avatar.py** - 服务 URL 使用环境变量
- [ ] **backend/services/redis_client.py** - Redis 配置使用环境变量
- [ ] **llm/milvus_config.py** - 端口改为 8602
- [ ] **llm/milvus_api_client.py** - 端口改为 8602
- [ ] **lip-sync/live_server.py** - 端口改为 8615

### 环境变量配置
- [ ] **创建 backend/.env** - 配置所有服务 URL 和端口
- [ ] **创建 llm/.env** - 配置 LLM 服务端口和 API
- [ ] **创建 rag/.env** - 配置 RAG 服务端口和路径
- [ ] **创建 lip-sync/.env** - 配置 Lip-Sync 端口
- [ ] **创建 tts/.env** - 配置 TTS 端口

### 创建必要的目录
```bash
mkdir -p backend/instance
mkdir -p rag/tmp
mkdir -p rag/chroma_db
mkdir -p rag/milvus_kb/KB
mkdir -p rag/multimodal_kb/KB
mkdir -p rag/multimodal_kb/dataset/imgs
```

---

## 🔧 推荐的修复顺序

1. **首先修复 lip-sync/lip-sync.json**（最关键）
2. **修复所有 TEMP_DIR 引用**（4 个文件）
3. **修复 RAG 配置文件中的路径**
4. **创建必要的目录**
5. **测试每个模块是否能启动**

---

## ⚡ 自动化修复建议

可以创建一个初始化脚本来自动处理这些配置：

```bash
#!/bin/bash
# init_config.sh

echo "🔧 初始化虚拟导师系统配置..."

# 1. 创建必要目录
echo "📁 创建目录..."
mkdir -p backend/instance
mkdir -p rag/tmp
mkdir -p rag/chroma_db
mkdir -p rag/milvus_kb/KB
mkdir -p rag/multimodal_kb/KB
mkdir -p rag/multimodal_kb/dataset/imgs

# 2. 检测 conda 路径
CONDA_BASE=$(conda info --base)
CONDA_INIT="$CONDA_BASE/etc/profile.d/conda.sh"
echo "✅ 检测到 Conda: $CONDA_INIT"

# 3. 获取当前目录
CURRENT_DIR=$(pwd)
LIPSYNC_DIR="$CURRENT_DIR/lip-sync"
echo "✅ 工作目录: $CURRENT_DIR"

# 4. 更新 lip-sync.json（需要手动确认）
echo "⚠️  请手动更新 lip-sync/lip-sync.json:"
echo "   conda_init: $CONDA_INIT"
echo "   working_directory: $LIPSYNC_DIR"

echo "✅ 初始化完成！"
```

---

**最后更新**: 2025年12月  
**优先级**: 🔴 高（必须修复才能运行）
