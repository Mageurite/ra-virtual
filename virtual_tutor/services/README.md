# Virtual Tutor Services

本目录包含 Virtual Tutor 系统的内部服务组件。

## 📁 服务列表

### 1. Lip-Sync Service (端口: 8615)
**功能**: Avatar 视频生成和实时渲染服务
- WebRTC 实时视频传输
- 嘴型同步（Lip-Sync）
- 支持多种 Avatar 模型（MuseTalk, Wav2Lip, UltraLight）

**启动命令**:
```bash
cd lip-sync
python live_server.py --port 8615
```

**环境变量配置**:
- 无需硬编码，所有配置通过命令行参数或配置文件
- 模型路径可通过环境变量 `MODEL_PATH` 指定

---

### 2. TTS Service (端口: 8604)
**功能**: 文本转语音合成服务
- Edge-TTS: 微软在线语音（免费）
- CosyVoice: 本地高质量 TTS
- GPT-SoVITS: 语音克隆
- Tacotron2: 经典 TTS 模型

**启动命令**:
```bash
cd tts
python tts.py --port 8604
```

**环境变量配置**:
- `TTS_MODEL_PATH`: TTS 模型目录
- `TTS_CACHE_DIR`: 音频缓存目录

---

## 🔧 配置说明

所有服务端口和路径均可通过以下方式配置：

1. **环境变量** (推荐)
2. **命令行参数**
3. **配置文件**

**不使用硬编码路径**，确保部署灵活性。

---

## 📦 依赖安装

每个服务有独立的 `requirements.txt`：

```bash
# Lip-Sync 服务
cd lip-sync
pip install -r requirements.txt

# TTS 服务
cd tts
pip install -r requirements.txt
```

---

## 🚀 与 Avatar Service 集成

Avatar Service (8001) 通过环境变量连接这些服务：

```bash
# avatar_service/.env
LIPSYNC_SERVICE_URL=http://localhost:8615
TTS_SERVICE_URL=http://localhost:8604
```

**灵活部署**:
- 本地开发: 使用 localhost
- Docker: 使用服务名称（如 `http://lipsync:8615`）
- 远程部署: 使用实际 IP 或域名

---

## 🐳 Docker 部署

每个服务都有 Dockerfile，可独立容器化部署：

```yaml
# docker-compose.yml 示例
services:
  lipsync:
    build: ./services/lip-sync
    ports:
      - "8615:8615"
    environment:
      - MODEL_PATH=/models
    volumes:
      - ./models:/models
  
  tts:
    build: ./services/tts
    ports:
      - "8604:8604"
    environment:
      - TTS_CACHE_DIR=/cache
    volumes:
      - ./tts-cache:/cache
```

---

## 📝 注意事项

1. **模型文件**: 需要单独下载模型文件到指定目录
2. **GPU 支持**: Lip-Sync 服务建议使用 GPU 加速
3. **端口配置**: 确保端口不冲突，可通过环境变量修改
4. **资源需求**: 
   - Lip-Sync: 4GB+ GPU 内存
   - TTS: 2GB+ RAM

---

## 🔗 相关文档

- [Lip-Sync README](lip-sync/README.md)
- [TTS README](tts/README.md)
- [Avatar Service README](../avatar_service/README.md)
- [系统部署指南](../DEPLOYMENT.md)
