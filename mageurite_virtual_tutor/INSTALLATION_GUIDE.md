# Virtual Tutor System - Complete Installation Guide

This guide provides step-by-step instructions to install and run all components of the Virtual Tutor System.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Module Installation](#module-installation)
   - [Backend Service](#1-backend-service)
   - [LLM Service](#2-llm-service)
   - [RAG Service](#3-rag-service)
   - [TTS Service](#4-tts-service)
   - [Lip-Sync Service](#5-lip-sync-service)
   - [Frontend](#6-frontend)
4. [Starting All Services](#starting-all-services)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Hardware Requirements

**Minimum Configuration** (Basic functionality):
- CPU: Intel i5 / AMD Ryzen 5 (4+ cores)
- RAM: 16GB
- GPU: NVIDIA GTX 1660 Ti (6GB VRAM)
- Storage: 50GB available space

**Recommended Configuration** (Full functionality with multiple users):
- CPU: Intel i7 / AMD Ryzen 7 (8+ cores)
- RAM: 32GB
- GPU: NVIDIA RTX 3090 (24GB VRAM)
- Storage: 100GB available space

### Software Requirements

- **Operating System**: Ubuntu 20.04/22.04 or macOS
- **CUDA**: 11.3+ (for GPU acceleration)
- **Python**: 3.10
- **Node.js**: 18+ (LTS version)
- **Conda**: Miniconda or Anaconda
- **FFmpeg**: Latest version
- **Ollama**: For LLM inference

---

## Prerequisites Installation

### 1. Install Conda

```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh

# Initialize conda
conda init bash
source ~/.bashrc
```

### 2. Install Node.js

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 3. Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg -y

# macOS
brew install ffmpeg
```

### 4. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Start Ollama service
ollama serve &

# Pull required models
ollama pull llama3.1:8b
ollama pull mistral-nemo:12b
```

### 5. Clone Repository

```bash
git clone https://github.com/Mageurite/virtual-tutor.git
cd virtual-tutor
```

### ⚠️ Important: Fix Hardcoded Paths

**Before proceeding with installation, please read [HARDCODED_ISSUES.md](./HARDCODED_ISSUES.md)**

The system contains several hardcoded paths that need to be updated for your environment, including:
- `lip-sync/lip-sync.json` - Conda paths and working directory (**must fix**)
- Temporary directory paths in `rag/app.py` and related files
- Database and model paths in RAG modules

See [HARDCODED_ISSUES.md](./HARDCODED_ISSUES.md) for a complete list and fix instructions.

---

## Module Installation

### 1. Backend Service

**Purpose**: Central coordinator for authentication, session management, and API routing

```bash
cd backend

# Create conda environment
conda create -n bread python=3.10 -y
conda activate bread

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print(f'Flask version: {flask.__version__}')"
```

**Configuration**:
- Edit `backend/config.py` if needed (JWT secret, database path, etc.)
- Database will be auto-created at `backend/instance/app.db` on first run

---

### 2. LLM Service

**Purpose**: Intelligent dialogue with RAG retrieval and web search capabilities

```bash
cd llm

# Use the same bread environment or create a new one
conda activate bread

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TAVILY_API_KEY="your_tavily_api_key_here"  # Get from tavily.com

# Verify installation
python -c "import langgraph; print('LangGraph installed successfully')"
```

**Note**: Tavily API key is optional - system will work without web search

---

### 3. RAG Service

**Purpose**: Knowledge retrieval from uploaded documents

```bash
cd rag

# Create RAG environment
conda create -n rag python=3.12 -y
conda activate rag

# Install poppler (required for PDF processing)
conda install -c conda-forge poppler -y

# Install Python dependencies
pip install -r requirements.txt

# Configure settings
# Edit config.py:
# - Set MODE to 0 (pure-text mode)
# - Update paths if needed

# Verify installation
python -c "import sentence_transformers; print('RAG dependencies OK')"
```

**Important**: Milvus vector database must be running. RAG service will start its own embedded Milvus instance.

---

### 4. TTS Service

**Purpose**: Text-to-speech audio generation (multiple engines supported)

```bash
cd tts

# Create TTS environment (separate for each engine if needed)
# For Edge-TTS (simplest, no GPU required)
conda create -n tts_edge python=3.10 -y
conda activate tts_edge
pip install edge-tts

# For other TTS engines, see tts/README.md
# - Tacotron2: Requires PyTorch + CUDA
# - GPT-SoVITS: Requires additional setup
# - CosyVoice: Requires additional setup

# Configure
# Edit tts/config.json and tts/model_info.json
```

**Quick Start**: Use Edge-TTS for fastest setup (no GPU required)

---

### 5. Lip-Sync Service

**Purpose**: Real-time avatar animation with lip-sync and WebRTC streaming

```bash
cd lip-sync

# Create environment
conda create -n nerfstream python=3.10 -y
conda activate nerfstream

# Install PyTorch (adjust CUDA version as needed)
# For CUDA 12.4:
conda install pytorch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 pytorch-cuda=12.4 -c pytorch -c nvidia

# For CUDA 11.8:
# conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia

# Install FFmpeg in conda env
conda install ffmpeg -y

# Install core dependencies
pip install -r requirements.txt

# Install MuseTalk dependencies
pip install --no-cache-dir -U openmim
mim install mmengine
mim install "mmcv==2.1.0"
mim install "mmdet==3.2.0" 
mim install "mmpose>=1.1.0"

# Download model files
# Download from: https://drive.google.com/file/d/18Cj9hTO5WcByMVQa2Q1OHKmK8JEsqISy/view
# Extract to lip-sync/models/ directory

# Configure lip-sync.json
# Edit the following fields:
# - conda_init: path to conda.sh (e.g., ~/miniconda3/etc/profile.d/conda.sh)
# - conda_env: nerfstream
# - working_directory: full path to lip-sync directory
```

**Model Download**: Required model files (~2GB) must be downloaded manually

---

### 6. Frontend

**Purpose**: React-based user interface

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react
```

**Configuration**:
- `frontend/src/config.js` contains API endpoints
- Adjust ports if services run on non-default ports

---

## Starting All Services

### Start Services in Order

Open **6 separate terminal windows/tabs** and run each service:

#### Terminal 1: Ollama (if not already running)
```bash
ollama serve
```

#### Terminal 2: LLM Service
```bash
cd llm
conda activate bread
gunicorn --config gunicorn_config.py "api_interface_optimized:app"

# OR for development:
# python api_interface_optimized.py
```

#### Terminal 3: RAG Service
```bash
cd rag
conda activate rag
python app.py
```

#### Terminal 4: TTS Service
```bash
cd tts
conda activate tts_edge  # or appropriate TTS environment

# For Edge-TTS:
python tts.py  # Follow tts/README.md for detailed startup

# The TTS service will start on configured port (default: 8604 for Edge-TTS)
```

#### Terminal 5: Lip-Sync Service
```bash
cd lip-sync
conda activate nerfstream
python app.py

# This starts the avatar server on port 8615+ (dynamic allocation)
```

#### Terminal 6: Backend
```bash
cd backend
conda activate bread
python run.py

# OR for production:
# gunicorn --config gunicorn_config.py "app:create_app()"
```

#### Terminal 7: Frontend
```bash
cd frontend
npm start

# Will open browser automatically at http://localhost:3000
```

---

## Verification

### Check Services Are Running

Run these commands in a new terminal:

```bash
# Check if ports are listening
lsof -i :3000   # Frontend (should show node)
lsof -i :8203   # Backend (should show python)
lsof -i :8611   # LLM (should show python)
lsof -i :8602   # RAG (should show python)
lsof -i :8604   # TTS (should show python)
lsof -i :8615   # Lip-Sync (should show python)

# Health check endpoints
curl http://localhost:8203/api/health   # Should return {"status": "ok"}
curl http://localhost:8611/health       # Should return health status
curl http://localhost:8602/health       # Should return health status
```

### Access the System

1. Open browser: http://localhost:3000
2. Register a new account or login
3. Try text chat first (simplest test)
4. Upload a document to test RAG
5. Try avatar interaction if all services are running

---

## Troubleshooting

### Service Won't Start

**Problem**: Module import errors
- **Solution**: Ensure correct conda environment is activated
- Check: `conda env list` to see all environments
- Verify: `which python` shows conda environment path

**Problem**: Port already in use
- **Solution**: 
  ```bash
  # Find process using port
  lsof -i :8203
  
  # Kill process
  kill -9 <PID>
  ```

**Problem**: CUDA out of memory
- **Solution**: 
  - Close other GPU applications
  - Use smaller LLM model: `ollama pull llama3.1:8b` instead of larger models
  - Reduce batch sizes in configuration

### Connection Issues

**Problem**: Frontend can't connect to backend
- Check `frontend/src/config.js` has correct backend URL
- Verify backend is running: `curl http://localhost:8203/api/health`
- Check CORS settings in `backend/app.py`

**Problem**: WebRTC video not showing
- Ensure lip-sync service is running
- Check browser console for errors
- Verify models are downloaded in `lip-sync/models/`

### Performance Issues

**Problem**: Slow LLM responses
- Check GPU utilization: `nvidia-smi`
- Ensure Ollama is using GPU: `ollama ps`
- Try smaller model or reduce context length

**Problem**: Avatar video lag
- Reduce video quality in lip-sync config
- Ensure adequate GPU VRAM available
- Check network bandwidth (for remote deployment)

---

## Quick Reference

### Default Ports
```
Frontend:      3000
Backend:       8203
LLM Service:   8611
RAG Service:   8602
TTS Service:   8604 (Edge-TTS), 8605 (Tacotron)
Lip-Sync:      8615+ (dynamic)
Ollama:        11434
```

### Conda Environments
```
bread       - Backend + LLM
rag         - RAG service
tts_edge    - TTS (Edge-TTS)
nerfstream  - Lip-Sync + Avatar
```

### Useful Commands

```bash
# List all conda environments
conda env list

# Activate environment
conda activate <env_name>

# Check what's using a port
lsof -i :<port>

# Check GPU status
nvidia-smi

# View service logs (if using systemd)
journalctl -u <service-name> -f
```

---

## Next Steps

After successful installation:

1. **Configure user accounts**: Create admin and regular users
2. **Upload knowledge base**: Add documents for RAG
3. **Create avatars**: Upload videos to create digital human avatars
4. **Test workflows**: Try different conversation scenarios
5. **Monitor performance**: Use provided test scripts in `test/` directory

For detailed API documentation, see `doc/` directory.

For module-specific details, refer to each module's README:
- [Backend README](backend/README.md)
- [LLM README](llm/README.md)
- [RAG README](rag/README.md)
- [TTS README](tts/README.md)
- [Lip-Sync README](lip-sync/README.md)
- [Frontend README](frontend/README.md)

---

**Last Updated**: December 2025  
**Version**: 2.0 (130f8ca)
