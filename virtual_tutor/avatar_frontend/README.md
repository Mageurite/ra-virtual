# Virtual Tutor - Avatar Frontend

## 📖 简介

这是一个极简的虚拟导师前端界面，只包含核心功能：
- 🎥 **视频对话** - 与 Avatar 导师实时视频互动
- 💬 **文字聊天** - 通过 LLM 进行智能对话

**无其他复杂功能** - 专注于学习体验本身。

---

## 🎯 功能特性

### 视频区域
- ✅ Avatar 实时视频显示
- ✅ WebRTC 连接/断开控制
- ✅ 连接状态指示器
- ✅ 优雅的加载动画

### 聊天区域
- ✅ 实时消息对话
- ✅ 流畅的动画效果
- ✅ 输入状态提示
- ✅ 对话历史记录
- ✅ 自动滚动到最新消息

---

## 🚀 快速开始

### 1. 启动后端服务

确保以下服务已启动：

```bash
# Web Backend (8000)
cd virtual_tutor/app_backend
uvicorn app.main:app --reload --port 8000

# Avatar Service (8001)
cd virtual_tutor/avatar_service
uvicorn main:app --reload --port 8001
```

### 2. 启动前端

**方法 1: 使用 Python HTTP 服务器**
```bash
cd virtual_tutor/avatar_frontend
python3 -m http.server 8080
```

**方法 2: 使用 Node.js**
```bash
cd virtual_tutor/avatar_frontend
npx http-server -p 8080
```

**方法 3: 直接打开 HTML**
```bash
# 直接在浏览器中打开
open index.html
```

### 3. 访问应用

打开浏览器访问：
```
http://localhost:8080
```

指定特定导师：
```
http://localhost:8080?tutor_id=1
```

---

## 📁 文件结构

```
avatar_frontend/
├── index.html       # 主页面（包含所有 HTML 和 CSS）
├── app.js          # 应用逻辑（JavaScript）
└── README.md       # 本文档
```

**极简设计** - 只有 3 个文件！

---

## ⚙️ 配置

在 `app.js` 中修改配置：

```javascript
const CONFIG = {
    // Web Backend API
    WEB_BACKEND_URL: 'http://localhost:8000',
    
    // Avatar Service API
    AVATAR_SERVICE_URL: 'http://localhost:8001',
    
    // 默认 Tutor ID
    TUTOR_ID: '1'
};
```

---

## 🎨 界面说明

### 左侧 - 视频区域
- **顶部**: 标题 + 连接状态指示器
  - 🔴 红点 = 未连接
  - 🟢 绿点 = 已连接
- **中间**: Avatar 视频画面
- **底部**: 连接/断开按钮

### 右侧 - 聊天区域
- **顶部**: 聊天标题
- **中间**: 消息列表
  - 左侧白色气泡 = 导师消息
  - 右侧紫色气泡 = 学生消息
- **底部**: 输入框 + 发送按钮

---

## 🔌 API 集成

### 使用的 API 端点

#### Web Backend (8000)
```javascript
// 获取 Tutor 信息
GET /api/tutors/{tutor_id}/info

// 健康检查
GET /api/tutors/{tutor_id}/health

// 发送聊天消息
POST /api/tutors/{tutor_id}/chat
Body: {
  message: "你好",
  conversation_history: []
}

// WebRTC 连接
POST /api/tutors/{tutor_id}/webrtc/offer
```

#### Avatar Service (8001)
```javascript
// TTS 语音合成（可选）
POST /api/tts/synthesize-json
Body: {
  text: "你好",
  engine: "edge-tts",
  voice: "zh-CN-XiaoxiaoNeural"
}
```

---

## 🎬 使用流程

### 学生使用步骤

1. **打开页面**
   - 浏览器访问应用
   - 系统自动检查服务状态

2. **连接 Avatar**
   - 点击"连接导师"按钮
   - 等待视频连接建立
   - 绿色指示灯表示连接成功

3. **开始对话**
   - 在聊天框输入问题
   - 按回车或点击"发送"
   - 查看导师回复

4. **结束会话**
   - 点击"断开连接"
   - 关闭浏览器标签

### 管理员准备工作

确保以下准备就绪：
1. ✅ Tutor 已创建（通过 Admin 后台）
2. ✅ Avatar 已创建并启动
3. ✅ Web Backend 和 Avatar Service 正常运行

---

## 🔧 自定义

### 修改颜色主题

在 `index.html` 的 `<style>` 中修改：

```css
/* 主色调 - 渐变紫色 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 改为渐变蓝色 */
background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

/* 改为渐变绿色 */
background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
```

### 修改默认语音

在 `app.js` 的 `syncAvatarSpeech()` 中：

```javascript
// 中文女声（默认）
voice: 'zh-CN-XiaoxiaoNeural'

// 中文男声
voice: 'zh-CN-YunxiNeural'

// 英文女声
voice: 'en-US-JennyNeural'
```

### 修改对话历史长度

在 `app.js` 的 `sendMessage()` 中：

```javascript
// 保留最近 10 条（默认）
conversation_history: conversationHistory.slice(-10)

// 保留最近 20 条
conversation_history: conversationHistory.slice(-20)

// 保留全部
conversation_history: conversationHistory
```

---

## 🐛 故障排查

### 问题 1: 无法连接 Avatar

**检查**:
```bash
# 检查 Web Backend
curl http://localhost:8000/health

# 检查 Avatar Service
curl http://localhost:8001/health

# 检查 Tutor 状态
curl http://localhost:8000/api/tutors/1/health
```

**解决**: 确保所有服务正常运行，Avatar 状态为 `running`。

### 问题 2: 聊天无响应

**检查**:
- 浏览器控制台是否有错误
- Web Backend 日志
- Avatar Service 日志

**解决**: 检查 LLM 服务（Ollama）是否正常。

### 问题 3: CORS 错误

**解决**: 在后端 `main.py` 中确认 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 4: WebRTC 连接失败

**检查**:
- 浏览器是否允许麦克风权限
- STUN 服务器是否可访问
- Avatar 是否真正在运行

**解决**: 确保 Mageurite Lip-Sync 服务 (8615) 正常运行。

---

## 📱 响应式设计

界面自动适配不同屏幕：

- **桌面 (> 1024px)**: 左右分屏布局
- **平板/手机 (< 1024px)**: 上下堆叠布局

---

## 🎯 下一步

### 可选增强功能

1. **流式聊天**
   - 实现打字机效果
   - 使用 SSE 接收流式响应

2. **语音输入**
   - 集成 Web Speech API
   - 点击麦克风说话

3. **多语言支持**
   - 添加语言切换按钮
   - 国际化 UI 文本

4. **聊天历史导出**
   - 添加"导出对话"按钮
   - 生成 PDF 或 TXT 文件

---

## 📝 许可

本项目是 Virtual Tutor 系统的一部分，遵循主项目许可协议。

---

## 💬 技术支持

遇到问题？
1. 查看浏览器控制台错误
2. 检查后端服务日志
3. 参考 [Avatar Service README](../avatar_service/README.md)
4. 参考 [Web Backend README](../app_backend/README.md)

---

**享受与虚拟导师的学习之旅！** 🚀
