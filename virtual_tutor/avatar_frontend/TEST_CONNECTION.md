# Frontend 与后端连接测试

## 🔗 API 连接关系

```
Avatar Frontend (8080)
    ↓
Web Backend (8000) - /api/tutors/{tutor_id}/*
    ↓
Avatar Service (8001) - /api/chat/*, /api/avatar/*, /api/tts/*
    ↓
External Services:
    - Ollama (11434)
    - Lip-Sync (8615)
    - TTS (8604)
```

---

## ✅ 前端调用的 API 端点

### 1. **健康检查**
```javascript
// 前端: checkServices()
GET http://localhost:8000/health
GET http://localhost:8001/health
GET http://localhost:8000/api/tutors/1/health
```

**对应后端路由**:
- ✅ `app_backend/app/main.py` → `/health`
- ✅ `avatar_service/main.py` → `/health`
- ✅ `routes_avatar_public.py` → `GET /{tutor_id}/health`

---

### 2. **获取导师信息**
```javascript
// 前端: connectAvatar()
GET http://localhost:8000/api/tutors/1/info
```

**对应后端路由**:
- ✅ `routes_avatar_public.py` → `GET /{tutor_id}/info`

**返回数据**:
```json
{
  "id": 1,
  "name": "Math Tutor",
  "description": "数学导师",
  "target_language": "zh-CN",
  "has_avatar": true,
  "avatar_status": "running"
}
```

---

### 3. **聊天对话**
```javascript
// 前端: sendMessage()
POST http://localhost:8000/api/tutors/1/chat
Body: {
  "message": "你好",
  "conversation_history": []
}
```

**对应后端路由**:
- ✅ `routes_avatar_public.py` → `POST /{tutor_id}/chat`
  - 代理到 → `Avatar Service` → `POST /api/chat/completion`

**返回数据**:
```json
{
  "response": "你好！我是你的虚拟导师...",
  "model": "mistral-nemo:12b",
  "usage": {...}
}
```

---

### 4. **WebRTC 连接**
```javascript
// 前端: initWebRTC()
POST http://localhost:8000/api/tutors/1/webrtc/offer
Body: {
  "sdp": "...",
  "type": "offer"
}
```

**对应后端路由**:
- ✅ `routes_avatar_public.py` → `POST /{tutor_id}/webrtc/offer`
  - 代理到 → `Avatar Service` → `POST /api/avatar/webrtc/offer`
    - 代理到 → `Lip-Sync Service` → `POST /offer`

---

### 5. **TTS 语音合成（可选）**
```javascript
// 前端: syncAvatarSpeech()
POST http://localhost:8001/api/tts/synthesize-json
Body: {
  "text": "你好",
  "engine": "edge-tts",
  "voice": "zh-CN-XiaoxiaoNeural"
}
```

**对应后端路由**:
- ✅ `avatar_service/tts/routes.py` → `POST /synthesize-json`

---

## 🧪 快速测试步骤

### 步骤 1: 启动所有服务

**终端 1 - Web Backend**:
```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend
source venv/bin/activate  # 如果有虚拟环境
uvicorn app.main:app --reload --port 8000
```

**终端 2 - Avatar Service**:
```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/avatar_service
source venv/bin/activate  # 如果有虚拟环境
uvicorn main:app --reload --port 8001
```

**终端 3 - Frontend**:
```bash
cd /Users/murphyxu/Code/ra/virtual_tutor/avatar_frontend
python3 -m http.server 8080
```

---

### 步骤 2: 浏览器测试

1. **打开浏览器**:
   ```
   http://localhost:8080
   ```

2. **打开开发者工具** (F12)

3. **查看控制台输出**:
   ```
   Virtual Tutor Frontend Initialized
   Tutor ID: 1
   ✓ Web Backend is ready
   ✓ Avatar Service is ready
   ```

4. **如果有错误**，会显示:
   ```
   Service check failed: TypeError: Failed to fetch
   ```

---

### 步骤 3: 手动 API 测试

**测试 1: 健康检查**
```bash
curl http://localhost:8000/health
# 预期: {"status":"ok"}

curl http://localhost:8001/health
# 预期: {"status":"ok","service":"avatar-ai-engine","version":"1.0.0"}
```

**测试 2: 导师信息（需要先创建 Tutor）**
```bash
curl http://localhost:8000/api/tutors/1/info
# 预期: {"id":1,"name":"...", ...}
# 错误: {"detail":"Tutor not found"} ← 需要先创建
```

**测试 3: 聊天对话**
```bash
curl -X POST http://localhost:8000/api/tutors/1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","conversation_history":[]}'
```

---

## 🐛 常见连接问题

### 问题 1: CORS 错误
```
Access to fetch at 'http://localhost:8000/health' from origin 'http://localhost:8080' has been blocked by CORS policy
```

**解决**: ✅ 已修复 - 在 `app_backend/app/main.py` 中添加了 `http://localhost:8080` 到 CORS 允许列表

---

### 问题 2: 404 Tutor not found
```json
{"detail":"Tutor not found"}
```

**原因**: 数据库中没有 Tutor 数据

**解决**: 需要先创建 Tutor（通过 Admin API 或直接插入数据库）
```bash
# 使用 psql 快速创建测试 Tutor
psql "postgresql://vtutor_user:password@localhost:5432/virtual_tutor"

INSERT INTO tutors (name, description, target_language, admin_id) 
VALUES ('Test Tutor', '测试导师', 'zh-CN', 1);
```

---

### 问题 3: 502 Avatar Service error
```json
{"detail":"Avatar Service error: Connection refused"}
```

**原因**: Avatar Service (8001) 未启动

**解决**: 
```bash
cd virtual_tutor/avatar_service
uvicorn main:app --reload --port 8001
```

---

### 问题 4: WebRTC 连接失败
```
Failed to send offer
```

**原因**: Lip-Sync 服务 (8615) 未启动

**解决**: 需要启动 Mageurite Lip-Sync 服务
```bash
cd mageurite/lip-sync
python live_server.py --port 8615
```

---

## 📊 完整调用流程示例

### 场景: 学生发送消息 "你好"

```
1. 前端 (8080)
   ↓ POST /api/tutors/1/chat
   Body: {"message": "你好"}

2. Web Backend (8000)
   ├─ 验证 Tutor ID=1 存在（查数据库）
   └─ 代理到 Avatar Service
      ↓ POST /api/chat/completion

3. Avatar Service (8001)
   ├─ 调用 LLM Service
   │  ↓ POST http://localhost:11434/api/generate
   └─ 返回 LLM 回复

4. Web Backend (8000)
   └─ 返回给前端

5. 前端 (8080)
   └─ 显示消息 "你好！我是你的虚拟导师..."
```

---

## ✅ 验证清单

- [ ] Web Backend 启动正常 (8000)
- [ ] Avatar Service 启动正常 (8001)
- [ ] Frontend 启动正常 (8080)
- [ ] CORS 已配置 `localhost:8080`
- [ ] 数据库中存在 Tutor 数据
- [ ] Ollama 服务运行中 (11434)
- [ ] 浏览器控制台无 CORS 错误
- [ ] 可以成功调用 `/health` 端点
- [ ] 可以获取 `/api/tutors/1/info`
- [ ] 可以发送聊天消息

---

## 🎯 下一步

如果所有检查通过，前端就能成功连接后端了！

如果需要 Avatar 视频功能，还需要额外启动：
- Mageurite Lip-Sync 服务 (8615)
- Mageurite TTS 服务 (8604)
