# Avatar + LLM 完整实现 - Quick Start

这是为 virtual_tutor 创建的独立 **Avatar + LLM** 服务实现，无多租户逻辑。

## 📦 已创建的模块

### 1. LLM 服务
- `services/llm_config.py` - LLM 配置管理
- `services/llm_service.py` - LLM 聊天服务（流式+非流式）
- `app/api/routes_chat.py` - LLM API 路由

### 2. Avatar 服务
- `services/avatar_config.py` - Avatar 配置管理
- `services/avatar_service.py` - Avatar 服务客户端
- `app/api/routes_avatars_simple.py` - Avatar API 路由（简化版）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend

# 添加到 requirements.txt
cat >> requirements.txt << 'EOF'
# LLM dependencies
langchain-ollama>=0.1.0
langchain-core>=0.2.0
langgraph>=0.0.50
tavily-python>=0.3.0  # Optional, for web search

# HTTP client
httpx>=0.24.0
EOF

# 安装
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件：

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_DEFAULT_MODEL=mistral-nemo:12b-instruct-2407-fp16
LLM_FALLBACK_MODEL=llama3.1:8b-instruct-q4_K_M
LLM_TEMPERATURE=0.4
ENABLE_STREAMING=true
GUARDRAIL_ENABLED=true

# RAG (Optional - 如果不使用可以不配置)
RAG_ENABLED=false
RAG_SERVICE_URL=http://localhost:8602

# Avatar/Lip-Sync Services  
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604
AVATAR_CREATE_TIMEOUT=200
AVATAR_START_TIMEOUT=300

# Tavily Search (Optional)
TAVILY_ENABLED=false
# TAVILY_API_KEY=your_key_here
```

### 3. 启动服务

#### Terminal 1 - Ollama (LLM)
```bash
# 确保 Ollama 运行
ollama serve

# 拉取模型（如果还没有）
ollama pull mistral-nemo:12b-instruct-2407-fp16
ollama pull llama3.1:8b-instruct-q4_K_M
```

#### Terminal 2 - Lip-Sync Service (从 mageurite)
```bash
cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor/lip-sync
conda activate nerfstream
python live_server.py
# 服务将运行在 http://localhost:8615
```

#### Terminal 3 - TTS Service (从 mageurite)
```bash
cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor/tts
conda activate tts_edge  # 或其他 TTS 环境
python tts.py
# 服务将运行在 http://localhost:8604
```

#### Terminal 4 - FastAPI Backend
```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend
uvicorn app.main:app --reload --port 8000
```

## 📖 API 使用示例

### LLM Chat API

#### 1. 流式聊天
```bash
curl -X POST "http://localhost:8000/api/chat/stream" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "What is machine learning?",
    "conversation_history": [],
    "stream": true
  }'
```

#### 2. 非流式聊天
```bash
curl -X POST "http://localhost:8000/api/chat/completion" \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "Explain neural networks in simple terms",
    "conversation_history": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi! How can I help?"}
    ]
  }'
```

#### 3. 检查 LLM 健康状态
```bash
curl "http://localhost:8000/api/chat/health"
```

#### 4. 列出可用模型
```bash
curl "http://localhost:8000/api/chat/models"
```

### Avatar API

#### 1. 列出 Avatars
```bash
curl "http://localhost:8000/api/avatars/list"
```

#### 2. 创建 Avatar
```bash
curl -X POST "http://localhost:8000/api/avatars/create" \\
  -F "name=my_teacher" \\
  -F "avatar_model=MuseTalk" \\
  -F "tts_model=edge-tts" \\
  -F "prompt_face=@/path/to/video.mp4"
```

#### 3. 启动 Avatar
```bash
curl -X POST "http://localhost:8000/api/avatars/start" \\
  -F "avatar_name=my_teacher"
```

#### 4. 获取 Avatar 预览
```bash
curl "http://localhost:8000/api/avatars/preview/my_teacher" --output preview.png
```

#### 5. 删除 Avatar
```bash
curl -X DELETE "http://localhost:8000/api/avatars/delete" \\
  -F "avatar_name=my_teacher"
```

#### 6. 检查 Avatar 服务健康状态
```bash
curl "http://localhost:8000/api/avatars/health"
```

## 🔧 前端集成示例

### React - LLM Chat
```javascript
// 流式聊天
async function streamChat(message, history) {
  const response = await fetch('http://localhost:8000/api/chat/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      message,
      conversation_history: history,
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        
        try {
          const json = JSON.parse(data);
          console.log(json.chunk);  // 处理文本块
        } catch (e) {}
      }
    }
  }
}
```

### React - Avatar Management
```javascript
// 创建 Avatar
async function createAvatar(name, videoFile) {
  const formData = new FormData();
  formData.append('name', name);
  formData.append('avatar_model', 'MuseTalk');
  formData.append('tts_model', 'edge-tts');
  formData.append('prompt_face', videoFile);

  const response = await fetch('http://localhost:8000/api/avatars/create', {
    method: 'POST',
    body: formData
  });

  return await response.json();
}

// 启动 Avatar
async function startAvatar(avatarName) {
  const formData = new FormData();
  formData.append('avatar_name', avatarName);

  const response = await fetch('http://localhost:8000/api/avatars/start', {
    method: 'POST',
    body: formData
  });

  return await response.json();
}
```

## 🎯 特性

### LLM 服务
- ✅ 流式和非流式响应
- ✅ 对话历史管理（保留最近 N 轮）
- ✅ 内容安全检查（Guardrail）
- ✅ 可选的 RAG 集成
- ✅ 支持自定义 System Prompt
- ✅ 多模型支持

### Avatar 服务
- ✅ 从视频创建 Avatar
- ✅ 支持多种模型（MuseTalk, Wav2Lip, UltraLight）
- ✅ 多种 TTS 模型（Edge-TTS, CosyVoice, GPT-SoVITS, Tacotron2）
- ✅ WebRTC 实时视频流
- ✅ Avatar 预览图
- ✅ 完整的生命周期管理

## ⚠️ 注意事项

1. **Avatar 创建时间**：根据视频长度，可能需要 30-60 秒
2. **Avatar 启动时间**：模型加载需要 1-5 分钟
3. **GPU 内存**：MuseTalk 需要较大 GPU 内存
4. **服务依赖**：Avatar 功能依赖 mageurite 的 lip-sync 和 TTS 服务

## 🐛 故障排除

### LLM 相关
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 检查模型是否可用
ollama list

# 测试 LLM API
curl http://localhost:8000/api/chat/health
```

### Avatar 相关
```bash
# 检查 Lip-Sync 服务
curl http://localhost:8615/avatar/get_avatars

# 检查 TTS 服务
curl http://localhost:8604/tts/models

# 测试 Avatar API
curl http://localhost:8000/api/avatars/health
```

## 📝 文档

- 完整 API 文档：http://localhost:8000/docs
- LLM 服务文档：查看 `services/llm_service.py`
- Avatar 服务文档：查看 `services/avatar_service.py`

所有代码都已经消除硬编码，使用环境变量配置，可以独立运行！
