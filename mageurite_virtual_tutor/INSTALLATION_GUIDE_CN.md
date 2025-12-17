# 虚拟导师系统 - 完整安装指南

本指南提供虚拟导师系统所有组件的分步安装和运行说明。

## 📋 目录

1. [系统要求](#系统要求)
2. [前置软件安装](#前置软件安装)
3. [模块安装](#模块安装)
   - [后端服务](#1-后端服务)
   - [LLM 服务](#2-llm-服务)
   - [RAG 服务](#3-rag-服务)
   - [TTS 服务](#4-tts-服务)
   - [唇形同步服务](#5-唇形同步服务)
   - [前端](#6-前端)
4. [启动所有服务](#启动所有服务)
5. [验证](#验证)
6. [故障排除](#故障排除)

---

## 系统要求

### 硬件要求

**最低配置**（基础功能）：
- CPU: Intel i5 / AMD Ryzen 5（4核及以上）
- 内存: 16GB
- GPU: NVIDIA GTX 1660 Ti（6GB 显存）
- 存储: 50GB 可用空间

**推荐配置**（完整功能，支持多用户）：
- CPU: Intel i7 / AMD Ryzen 7（8核及以上）
- 内存: 32GB
- GPU: NVIDIA RTX 3090（24GB 显存）
- 存储: 100GB 可用空间

### 软件要求

- **操作系统**: Ubuntu 20.04/22.04 或 macOS
- **CUDA**: 11.3+（GPU 加速必需）
- **Python**: 3.10
- **Node.js**: 18+（LTS 版本）
- **Conda**: Miniconda 或 Anaconda
- **FFmpeg**: 最新版本
- **Ollama**: 用于 LLM 推理

---

## 前置软件安装

### 1. 安装 Conda

```bash
# 下载 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装
bash Miniconda3-latest-Linux-x86_64.sh

# 初始化 conda
conda init bash
source ~/.bashrc
```

### 2. 安装 Node.js

```bash
# 使用 nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 3. 安装 FFmpeg

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg -y

# macOS
brew install ffmpeg
```

### 4. 安装 Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# 启动 Ollama 服务
ollama serve &

# 拉取所需模型
ollama pull llama3.1:8b
ollama pull mistral-nemo:12b
```

### 5. 克隆仓库

```bash
git clone https://github.com/Mageurite/virtual-tutor.git
cd virtual-tutor
```

### ⚠️ 重要：修复硬编码路径

**在开始安装前，请先阅读 [HARDCODED_ISSUES.md](./HARDCODED_ISSUES.md)**

系统中存在一些硬编码的路径需要根据你的环境修改，主要包括：
- `lip-sync/lip-sync.json` - Conda 路径和工作目录（**必须修改**）
- `rag/app.py` 等文件中的临时目录路径
- RAG 模块中的数据库和模型路径

详细的问题清单和修复方法请参见 [HARDCODED_ISSUES.md](./HARDCODED_ISSUES.md)

---

## 模块安装

### 1. 后端服务

**用途**：中央协调器，负责身份验证、会话管理和 API 路由

```bash
cd backend

# 创建 conda 环境
conda create -n bread python=3.10 -y
conda activate bread

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import flask; print(f'Flask 版本: {flask.__version__}')"
```

**配置说明**：
- 如需要可编辑 `backend/config.py`（JWT 密钥、数据库路径等）
- 首次运行时会自动在 `backend/instance/app.db` 创建数据库

---

### 2. LLM 服务

**用途**：智能对话，支持 RAG 检索和网络搜索

```bash
cd llm

# 使用相同的 bread 环境或创建新环境
conda activate bread

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TAVILY_API_KEY="your_tavily_api_key_here"  # 从 tavily.com 获取

# 验证安装
python -c "import langgraph; print('LangGraph 安装成功')"
```

**注意**：Tavily API 密钥是可选的 - 没有它系统仍可工作，只是无法进行网络搜索

---

### 3. RAG 服务

**用途**：从上传的文档中进行知识检索

```bash
cd rag

# 创建 RAG 环境
conda create -n rag python=3.12 -y
conda activate rag

# 安装 poppler（PDF 处理必需）
conda install -c conda-forge poppler -y

# 安装 Python 依赖
pip install -r requirements.txt

# 配置设置
# 编辑 config.py:
# - 将 MODE 设置为 0（纯文本模式）
# - 如需要更新路径

# 验证安装
python -c "import sentence_transformers; print('RAG 依赖安装完成')"
```

**重要**：Milvus 向量数据库必须运行。RAG 服务会启动自己的嵌入式 Milvus 实例。

---

### 4. TTS 服务

**用途**：文本转语音，支持多种引擎

```bash
cd tts

# 为 Edge-TTS 创建环境（最简单，无需 GPU）
conda create -n tts_edge python=3.10 -y
conda activate tts_edge
pip install edge-tts

# 对于其他 TTS 引擎，请参见 tts/README.md
# - Tacotron2: 需要 PyTorch + CUDA
# - GPT-SoVITS: 需要额外设置
# - CosyVoice: 需要额外设置

# 配置
# 编辑 tts/config.json 和 tts/model_info.json
```

**快速开始**：使用 Edge-TTS 最快（无需 GPU）

---

### 5. 唇形同步服务

**用途**：实时数字人动画，支持唇形同步和 WebRTC 视频流

```bash
cd lip-sync

# 创建环境
conda create -n nerfstream python=3.10 -y
conda activate nerfstream

# 安装 PyTorch（根据你的 CUDA 版本调整）
# CUDA 12.4:
conda install pytorch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 pytorch-cuda=12.4 -c pytorch -c nvidia

# CUDA 11.8:
# conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia

# 在 conda 环境中安装 FFmpeg
conda install ffmpeg -y

# 安装核心依赖
pip install -r requirements.txt

# 安装 MuseTalk 依赖
pip install --no-cache-dir -U openmim
mim install mmengine
mim install "mmcv==2.1.0"
mim install "mmdet==3.2.0" 
mim install "mmpose>=1.1.0"

# 下载模型文件
# 下载地址: https://drive.google.com/file/d/18Cj9hTO5WcByMVQa2Q1OHKmK8JEsqISy/view
# 解压到 lip-sync/models/ 目录

# 配置 lip-sync.json
# 编辑以下字段:
# - conda_init: conda.sh 路径（如 ~/miniconda3/etc/profile.d/conda.sh）
# - conda_env: nerfstream
# - working_directory: lip-sync 目录的完整路径
```

**模型下载**：必须手动下载所需的模型文件（约 2GB）

---

### 6. 前端

**用途**：基于 React 的用户界面

```bash
cd frontend

# 安装依赖
npm install

# 验证安装
npm list react
```

**配置说明**：
- `frontend/src/config.js` 包含 API 端点配置
- 如果服务运行在非默认端口，需要调整端口

---

## 启动所有服务

### 按顺序启动服务

打开 **7 个独立的终端窗口/标签页**，分别运行每个服务：

#### 终端 1: Ollama（如果尚未运行）
```bash
ollama serve
```

#### 终端 2: LLM 服务
```bash
cd llm
conda activate bread
gunicorn --config gunicorn_config.py "api_interface_optimized:app"

# 或者用于开发:
# python api_interface_optimized.py
```

#### 终端 3: RAG 服务
```bash
cd rag
conda activate rag
python app.py
```

#### 终端 4: TTS 服务
```bash
cd tts
conda activate tts_edge  # 或适当的 TTS 环境

# 对于 Edge-TTS:
python tts.py  # 详细启动方法参见 tts/README.md

# TTS 服务将在配置的端口启动（Edge-TTS 默认: 8604）
```

#### 终端 5: 唇形同步服务
```bash
cd lip-sync
conda activate nerfstream
python app.py

# 这会在 8615+ 端口启动数字人服务器（动态分配）
```

#### 终端 6: 后端
```bash
cd backend
conda activate bread
python run.py

# 或者用于生产环境:
# gunicorn --config gunicorn_config.py "app:create_app()"
```

#### 终端 7: 前端
```bash
cd frontend
npm start

# 会自动在浏览器中打开 http://localhost:3000
```

---

## 验证

### 检查服务是否运行

在新终端中运行以下命令：

```bash
# 检查端口是否在监听
lsof -i :3000   # 前端（应显示 node）
lsof -i :8203   # 后端（应显示 python）
lsof -i :8611   # LLM（应显示 python）
lsof -i :8602   # RAG（应显示 python）
lsof -i :8604   # TTS（应显示 python）
lsof -i :8615   # 唇形同步（应显示 python）

# 健康检查端点
curl http://localhost:8203/api/health   # 应返回 {"status": "ok"}
curl http://localhost:8611/health       # 应返回健康状态
curl http://localhost:8602/health       # 应返回健康状态
```

### 访问系统

1. 打开浏览器：http://localhost:3000
2. 注册新账户或登录
3. 首先尝试文本聊天（最简单的测试）
4. 上传文档测试 RAG
5. 如果所有服务都在运行，尝试数字人交互

---

## 故障排除

### 服务无法启动

**问题**：模块导入错误
- **解决方案**：确保激活了正确的 conda 环境
- 检查：`conda env list` 查看所有环境
- 验证：`which python` 显示 conda 环境路径

**问题**：端口已被占用
- **解决方案**：
  ```bash
  # 查找使用端口的进程
  lsof -i :8203
  
  # 终止进程
  kill -9 <PID>
  ```

**问题**：CUDA 内存不足
- **解决方案**：
  - 关闭其他 GPU 应用
  - 使用更小的 LLM 模型：`ollama pull llama3.1:8b` 而不是更大的模型
  - 在配置中减小批处理大小

### 连接问题

**问题**：前端无法连接到后端
- 检查 `frontend/src/config.js` 是否有正确的后端 URL
- 验证后端正在运行：`curl http://localhost:8203/api/health`
- 检查 `backend/app.py` 中的 CORS 设置

**问题**：WebRTC 视频不显示
- 确保唇形同步服务正在运行
- 检查浏览器控制台是否有错误
- 验证模型已下载到 `lip-sync/models/`

### 性能问题

**问题**：LLM 响应缓慢
- 检查 GPU 使用率：`nvidia-smi`
- 确保 Ollama 正在使用 GPU：`ollama ps`
- 尝试更小的模型或减少上下文长度

**问题**：数字人视频卡顿
- 在唇形同步配置中降低视频质量
- 确保有足够的 GPU 显存可用
- 检查网络带宽（用于远程部署）

---

## 快速参考

### 默认端口
```
前端:          3000
后端:          8203
LLM 服务:      8611
RAG 服务:      8602
TTS 服务:      8604 (Edge-TTS), 8605 (Tacotron)
唇形同步:      8615+（动态分配）
Ollama:       11434
```

### Conda 环境
```
bread       - 后端 + LLM
rag         - RAG 服务
tts_edge    - TTS（Edge-TTS）
nerfstream  - 唇形同步 + 数字人
```

### 常用命令

```bash
# 列出所有 conda 环境
conda env list

# 激活环境
conda activate <环境名>

# 检查端口占用
lsof -i :<端口>

# 检查 GPU 状态
nvidia-smi

# 查看服务日志（如果使用 systemd）
journalctl -u <服务名> -f
```

---

## 下一步

成功安装后：

1. **配置用户账户**：创建管理员和普通用户
2. **上传知识库**：为 RAG 添加文档
3. **创建数字人**：上传视频创建数字人形象
4. **测试工作流**：尝试不同的对话场景
5. **监控性能**：使用 `test/` 目录中提供的测试脚本

详细 API 文档请参见 `doc/` 目录。

各模块详细信息请参考各模块的 README：
- [后端 README](backend/README.md)
- [LLM README](llm/README.md)
- [RAG README](rag/README.md)
- [TTS README](tts/README.md)
- [唇形同步 README](lip-sync/README.md)
- [前端 README](frontend/README.md)

---

**最后更新**: 2025年12月  
**版本**: 2.0 (130f8ca)
