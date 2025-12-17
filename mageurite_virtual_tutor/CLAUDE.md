# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Virtual Tutor System** - An AI-powered educational platform that combines real-time digital avatars with intelligent conversation capabilities. The system integrates MuseTalk lip-sync technology, streaming LLM responses, and RAG-enhanced knowledge retrieval to create an immersive learning experience.

**Repository**: https://github.com/Mageurite/virtual-tutor.git  
**Current Version**: 130f8ca (Avatar video connection fix)  
**Team**: UNSW CSE COMP9900 - Team H15A_BREAD

**Technology Stack**: 
- **Frontend**: React 19.1.0 + WebRTC + Server-Sent Events (SSE)
- **Backend**: Flask 3.1.1 + Gunicorn + SQLAlchemy + Redis
- **LLM**: LangGraph + Ollama (llama3.1:8b, mistral-nemo:12b) + Tavily Search
- **RAG**: Milvus vector database + SentenceTransformers
- **Lip-Sync/Avatar**: MuseTalk + PyTorch + aiortc (WebRTC) - integrated in lip-sync module
- **TTS**: Edge-TTS, Tacotron2, GPT-SoVITS, CosyVoice

## Architecture

This is a **modular microservices architecture** with loosely coupled components communicating via HTTP/WebSocket APIs:

```
┌──────────────────────────────────────────────────────────────┐
│                   Frontend (React:3000)                      │
│  - Chat Interface with SSE streaming                         │
│  - WebRTC Video Display (Avatar)                             │
│  - User Management & Authentication                          │
└────────────┬──────────────────────────────┬──────────────────┘
             │ HTTP/SSE                     │ WebRTC
             ↓                              ↓
┌────────────────────────────┐   ┌────────────────────────────┐
│   Backend (Flask:8203)     │   │  Lip-Sync Service (8615+)  │
│   ├─ Gunicorn workers      │   │  ├─ MuseTalk lip-sync      │
│   ├─ JWT Authentication    │   │  ├─ WebRTC streaming       │
│   ├─ SQLite Database       │   │  ├─ Avatar management      │
│   └─ Redis (optional)      │   │  └─ Multi-user support     │
└─────┬──────┬──────┬────────┘   └────────────────────────────┘
      │      │      │
      ↓      ↓      ↓
┌─────────┐ ┌────────┐ ┌───────────┐
│   LLM   │ │  RAG   │ │    TTS    │
│  :8611  │ │ :8602  │ │ :8604/5   │
│         │ │        │ │           │
│ LangGra │ │ Milvus │ │ Edge-TTS  │
│   ph    │ │ Vector │ │ Tacotron  │
│ Ollama  │ │   DB   │ │ GPT-VITS  │
└─────────┘ └────────┘ └───────────┘
```

### Key Design Patterns

1. **Backend as Central Coordinator**
   - Flask backend handles all API requests and authentication
   - Coordinates between LLM, RAG, TTS, and Lip-Sync services
   - SQLite for user data, sessions, and chat history
   - Optional Redis for session state and caching

2. **Lip-Sync Service (Integrated Avatar Management)**
   - Located in `lip-sync/` directory
   - Handles avatar creation, lip-sync generation, and WebRTC streaming
   - Each user can have dedicated avatar instances
   - Based on LiveTalking and MuseTalk projects

3. **Streaming Architecture**
   - LLM responses stream via Server-Sent Events (SSE)
   - Text chunks forwarded to TTS for low-latency audio generation
   - Avatar lip-sync runs in real-time with incoming TTS audio
   - Frontend receives and displays streaming responses

4. **WebRTC Video Streaming**
   - Lip-sync service provides WebRTC endpoints for video
   - Frontend connects directly to lip-sync service for video feed
   - Audio-driven facial animation synchronized with TTS output

5. **RAG Integration with Knowledge Bases**
   - User-specific knowledge base (personal uploads via backend)
   - Public knowledge base (shared documents)
   - Query classification: RAG retrieval / Web search / Direct answer
   - Milvus vector database for semantic search

## Quick Start

### Prerequisites
- **Hardware**: NVIDIA GPU with 24GB+ VRAM recommended (for lip-sync and LLM)
- **Software**: Python 3.10+, Node.js 18+, Ollama, FFmpeg
- **Conda Environments**: 
  - `bread` (backend + llm)
  - `rag` (RAG service)
  - `nerfstream` (lip-sync service)
  - Additional envs for TTS models (optional)

### Installation Overview

**IMPORTANT**: Each module must be set up independently with its own conda environment. Follow the detailed installation steps in each module's README.

### Start All Services (After Installation)

```bash
# 1. Start Ollama (for LLM)
ollama serve &

# 2. Start LLM Service (conda env: bread or rag)
cd llm
conda activate bread
gunicorn --config gunicorn_config.py "api_interface_optimized:app" &

# 3. Start RAG Service (conda env: rag)
cd rag
conda activate rag
python app.py &

# 4. Start TTS Service (conda env: varies by TTS engine)
cd tts
# Follow tts/README.md for specific TTS engine startup

# 5. Start Lip-Sync Service (conda env: nerfstream)
cd lip-sync
conda activate nerfstream
python app.py &

# 6. Start Backend (conda env: bread)
cd backend
conda activate bread
python run.py &
# OR for production: gunicorn --config gunicorn_config.py "app:create_app()"

# 7. Start Frontend
cd frontend
npm start
```

### Access System
- Frontend: http://localhost:3000
- Backend API: http://localhost:8203
- LLM Service: http://localhost:8611
- RAG Service: http://localhost:8602
- TTS Service: http://localhost:8604 (Edge-TTS) or 8605 (Tacotron)
- Lip-Sync: http://localhost:8615+ (dynamic ports)

### Health Checks
```bash
curl http://localhost:8203/api/health     # Backend
curl http://localhost:8611/health         # LLM
curl http://localhost:8602/health         # RAG
```

## Development Commands

### Backend (`backend/`)

**Environment**: Conda `bread` environment

```bash
cd backend

# Create conda environment
conda create -n bread python=3.10 -y
conda activate bread

# Install dependencies
pip install -r requirements.txt

# Development mode (auto-reload)
python run.py

# Production mode
gunicorn --config gunicorn_config.py "app:create_app()"

# Run single test
python tests/test_login.py

# Database initialization (SQLite auto-created at instance/app.db)
```

**Common Backend Tasks**:
- Database: SQLite at `backend/instance/app.db` (auto-created)
- Uploads: Files stored in `backend/uploads/{user_id}/`
- Logs: Check `logs/backend.log`

### Frontend (`frontend/`)

```bash
cd frontend

# Install dependencies
npm install

# Development server (port 3000)
npm start

# Production build
npm run build

# Regenerate config after port changes
cd .. && python scripts/generate_frontend_config.py
```

**Important Files**:
- `src/config.js` - Auto-generated from `ports_config.py`
- `src/components/ChatInterface.js` - Main chat UI
- `src/components/VideoAvatar.js` - WebRTC avatar display
- `src/services/webrtcService.js` - WebRTC connection logic

### LLM Service (`llm/`)

**Environment**: Conda `bread` or `rag` environment

```bash
cd llm

# Install dependencies
pip install -r requirements.txt

# Start service (production)
gunicorn --config gunicorn_config.py "api_interface_optimized:app"

# Test LLM latency
cd ../test
python test_current.py

# Test with safeguard
python test/test_safeguard.py
```

**Key Files**:
- `ai_assistant_optimized.py` - LangGraph orchestration logic
- `api_interface_optimized.py` - FastAPI/Flask endpoints
- `milvus_api_client.py` - RAG retrieval integration

### RAG Service (`rag/`)

**Environment**: Conda `rag` environment

```bash
cd rag

# Install dependencies
pip install -r requirements.txt

# Start service
python app.py

# Test RAG workflow
cd ../test
python test_rag_integration.py
```

### Lip-Sync Module (`lip-sync/`)

**Environment**: Conda `nerfstream` environment

```bash
cd lip-sync

# Create conda environment
conda create -n nerfstream python=3.10 -y
conda activate nerfstream

# Install PyTorch (adjust for your CUDA version)
conda install pytorch==2.5.0 torchvision==0.20.0 torchaudio==2.5.0 pytorch-cuda=12.4 -c pytorch -c nvidia

# Install dependencies
pip install -r requirements.txt

# Install MuseTalk dependencies
conda install ffmpeg
pip install --no-cache-dir -U openmim
mim install mmengine
mim install "mmcv==2.1.0"
mim install "mmdet==3.2.0"
mim install "mmpose>=1.1.0"

# Download model files (see lip-sync/README.md)

# Start lip-sync server
python app.py
```

### Testing (`test/`)

**Important**: Generate JWT token first (one-time setup):
```bash
conda activate bread
python test/generate_test_token.py
```

**Run Tests** (any Python environment):
```bash
# Backend performance & QPS
python test/test_concurrency.py quick

# RAG workflow end-to-end
python test/test_rag_integration.py

# Avatar management
python test/test_manager.py

# LLM service latency
python test/test_current.py

# List all tests
ls test/test_*.py
```

## Core Components

### Backend (`backend/`)

**Technology**: Flask 3.1.1 + Gunicorn + SQLAlchemy + Redis

**Directory Structure**:
```
backend/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── gunicorn_config.py     # Multi-worker configuration
├── models/
│   ├── user.py           # User database model
│   └── ...
├── routes/
│   ├── auth.py           # Authentication endpoints
│   ├── chat.py           # Chat/LLM endpoints
│   ├── avatar.py         # Avatar management proxy
│   ├── upload.py         # File upload & RAG indexing
│   ├── user.py           # User management
│   └── admin.py          # Admin operations
├── services/
│   ├── email_service.py  # Email notifications
│   └── http_client.py    # HTTP client wrapper
└── instance/
    └── app.db            # SQLite database (auto-created)
```

**API Endpoints**:
```
POST   /api/auth/login              # User authentication (JWT)
POST   /api/auth/register           # User registration
POST   /api/file/upload             # Upload docs for RAG
GET    /api/chat                    # Chat interface
POST   /api/chat/stream             # Streaming chat (SSE)
GET    /api/user/profile            # User profile
POST   /api/avatar/upload           # Upload avatar video
GET    /api/health                  # Health check
```

**Multi-Tenant Architecture**:
- Database models support Admin → Tutor → Student hierarchy
- User isolation via foreign key relationships
- JWT tokens contain user_id and role for authorization

### Frontend (`frontend/`)

**Technology**: React 19.1.0 + WebRTC + SSE

**Key Components**:
- `ChatInterface.js` - Streaming chat with message history
- `VideoAvatar.js` - WebRTC video display with connection management
- `webrtcService.js` - WebRTC signaling and peer connection
- **Tab lock mechanism** prevents multi-tab conflicts

**Configuration**:
- `src/config.js` is auto-generated from `ports_config.py`
- After changing ports, run: `python scripts/generate_frontend_config.py`

### LLM Service (`llm/`)

**Technology**: LangGraph + Ollama + Tavily Search

**Workflow**:
```
User Query → Query Classification → Tool Selection
                                    ↓
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
              RAG Retrieval   Web Search   Direct Answer
                    │               │               │
                    └───────────────┼───────────────┘
                                    ↓
                          LLM Response Generation
                                    ↓
                         Streaming to Frontend (SSE)
```

**Performance**:
- Target TTFT (Time-To-First-Token): <1 second
- Typical response speed: 130+ chars/sec
- Content safety filtering via safeguard module

### RAG Service (`rag/`)

**Technology**: Milvus + SentenceTransformers + ChromaDB

**Features**:
- Document embedding and vector storage
- User-specific and public knowledge bases
- Semantic similarity search with configurable top-k
- Supports PDF, TXT, DOCX formats

**API**:
```
POST /api/upload_file          # Index document into Milvus
POST /api/search               # Semantic search
GET  /api/list_files           # List indexed documents
POST /api/delete_file          # Remove from knowledge base
```

### Lip-Sync Module (`lip-sync/`)

**Technology**: MuseTalk + PyTorch + WebRTC (aiortc) + LiveTalking

**Features**:
- Real-time facial animation generation with MuseTalk
- Audio-driven lip-sync
- Avatar instance management (multiple concurrent users)
- Multiple TTS engine support (Edge-TTS, Tacotron, GPT-SoVITS, CosyVoice)
- WebRTC video streaming
- Background blur processing
- Video upload and avatar creation

**Key Files**:
- `app.py` - Main avatar server entry point
- `live_server.py` - Avatar instance server
- `create_avatar.py` - Avatar creation from video uploads
- `musereal.py` - MuseTalk integration for lip-sync
- `ttsreal.py` - TTS integration
- `webrtc.py` - WebRTC signaling and streaming
- `lip-sync.json` - Configuration file

**Avatar Instance Management**:
- Each user can have dedicated avatar instances
- Dynamic port allocation starting from 8615
- GPU-accelerated rendering for real-time performance

### TTS Module (`tts/`)

**Supported Engines**:
- **Edge-TTS**: Microsoft voices, 50+ languages
- **Tacotron2**: Custom voice training
- **GPT-SoVITS**: Few-shot voice cloning
- **CosyVoice**: High-quality multilingual synthesis

**Default Ports**:
- Edge-TTS: 8604
- Tacotron: 8605

## Configuration Management

### Port Configuration

**Default Service Ports**:

```
Frontend:        3000
Backend:         8203
LLM Service:     8611
RAG Service:     8602
TTS Edge-TTS:    8604
TTS Tacotron:    8605
Lip-Sync Base:   8615+ (dynamic)
Ollama:          11434
Milvus:          19530
```

**Configuration Files**:
- `backend/config.py` - Backend configuration
- `lip-sync/lip-sync.json` - Lip-sync module configuration
- `tts/config.json` - TTS service configuration
- `tts/model_info.json` - TTS model metadata
- `frontend/src/config.js` - Frontend API endpoints

### Environment Variables

**Backend** (`.env` in `backend/`):
```bash
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRY_HOURS=5
LLM_SERVICE_URL=http://localhost:8611
RAG_SERVICE_URL=http://localhost:8602
AVATAR_MANAGER_URL=http://localhost:8607
REDIS_HOST=localhost
REDIS_PORT=6379
```

**LLM Service** (`.env` in `llm/`):
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
TAVILY_API_KEY=your-tavily-api-key
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

## Database Schema

**Current**: SQLite at `backend/instance/app.db` (auto-created by Flask-SQLAlchemy)

**Existing Models** (`backend/models/`):
- **User**: Basic user accounts with email/password authentication
  - Fields: id, email, hashed_password, username, avatar_url, created_at
  - No multi-tenancy yet (single-user mode)

**Planned Multi-Tenant Models** (to integrate from virtual_tutor):
- **Admin**: System administrators who manage tutors
- **Tutor**: Educators who create learning sessions
- **Student**: Learners under specific tutors (tutor_id foreign key)
- **Session**: Track learning sessions (tutor_id, student_id, engine_url, engine_token)
- **ChatMessage**: Conversation history with role (student/assistant/system)
- **RAGDocument**: Document metadata for knowledge base

**Migration Path**:
1. Add multi-tenant models from `virtual_tutor/app_backend/app/models/`
2. Implement Alembic migrations for schema changes
3. Update authentication to support admin/student JWT roles
4. Enhance API routes with multi-tenant filtering

## Authentication & Security

**JWT Authentication**:
- Algorithm: HS256
- Token format: `{"sub": user_id, "role": "admin"/"student"}`
- Expiry: Configurable (default 5 hours)

**OAuth2 Flow**:
- Admin: `POST /api/auth/login` with email/password
- Returns: `{"access_token": "...", "token_type": "bearer"}`

**Multi-Tenant Security**:
- All queries filtered by ownership chain (Admin → Tutor → Student)
- JWT role-based access control
- Cross-tenant data access prevention

## Deployment Notes

**Why No Docker?**
1. High hardware requirements (~40GB GPU VRAM)
2. Client preference for non-containerized deployment
3. Approved by course coordinator with detailed installation docs

**Production Deployment**:
- Use Gunicorn with multiple workers
- Configure CORS to restrict origins
- Use PostgreSQL instead of SQLite for production
- Set strong JWT secret keys
- Configure proper logging and monitoring

## Special Conventions

### Streaming Chat Pattern
```python
# Backend forwards LLM stream to frontend via SSE
def stream_response():
    for chunk in llm_response:
        yield f"data: {json.dumps(chunk)}\n\n"

        # Forward text chunks to TTS for low-latency audio
        if word_count % 5 == 0:
            send_to_tts(accumulated_text)
```

### Avatar Creation Pattern
```python
# Upload video file and create avatar
# lip-sync/create_avatar.py handles video processing
# Extracts video, processes with MuseTalk
# Stores avatar data for later use
```

### WebRTC Streaming Pattern
```python
# Lip-sync service provides WebRTC endpoints
# Frontend connects directly for video feed
# aiortc handles WebRTC signaling and media
```

## Integration with Summer0310/virtual_tutor.git

The `Summer0310/virtual_tutor` repository (branch: `feat/backend-student-auth`) provides a **production-ready multi-tenant backend** with complete authentication and session management.

### What virtual_tutor Provides

**Architecture**:
- FastAPI backend with SQLAlchemy 2.0 and Alembic migrations
- React frontend with Material-UI components
- Dual OAuth2 authentication (admin + student)
- Session and chat message tracking

**Data Model**:
```
Admin (id, email, hashed_password)
  ↓ (1:N)
Tutor (id, admin_id, name, description, target_language)
  ↓ (1:N)
Student (id, tutor_id, email, name, hashed_password, is_active)
  ↓ (1:N)
Session (id, tutor_id, student_id, engine_url, engine_token, status)
  ↓ (1:N)
ChatMessage (id, session_id, role, content, created_at)
```

**Authentication**:
- Separate OAuth2 flows for admin and student
- JWT tokens with role claims: `{"sub": user_id, "role": "admin"|"student"}`
- Token-based dependency injection for current_user

### Integration Strategy

**Phase 1: Adapt Models** (Priority: High)
1. Convert FastAPI models to Flask-SQLAlchemy:
   - `virtual_tutor/app_backend/app/models/*.py` → `mageurite/backend/models/*.py`
   - Keep relationships and foreign key constraints
   - Adapt Column types (FastAPI DateTime → Flask DateTime)

2. Add Alembic migrations:
   ```bash
   cd backend
   flask db init
   flask db migrate -m "Add multi-tenant models"
   flask db upgrade
   ```

**Phase 2: Enhance Authentication** (Priority: High)
1. Implement dual authentication in `backend/routes/auth.py`:
   - `POST /api/auth/admin/login` - Admin login with email/password
   - `POST /api/auth/student/login` - Student login with email/password
   
2. Add JWT role-based authorization:
   - Create decorators: `@require_admin`, `@require_student`
   - Update JWT payload: `{"sub": user_id, "role": "admin"|"student", "tutor_id": ...}`

**Phase 3: Add Multi-Tenant APIs** (Priority: Medium)
1. Admin APIs:
   - `GET /api/admin/tutors` - List tutors for current admin
   - `POST /api/admin/tutors/{id}/students` - Add student to tutor
   
2. Student APIs:
   - `POST /api/student/sessions` - Create new learning session
   - `GET /api/student/sessions/{id}/messages` - Get chat history

**Phase 4: Connect with AI Engine** (Priority: Medium)
1. Modify Session creation to:
   - Call Avatar Manager to launch avatar instance
   - Store `engine_url` and `engine_token` in Session model
   - Return to frontend for WebRTC connection

2. Update ChatMessage to integrate with:
   - LLM streaming responses
   - RAG retrieval per tutor's knowledge base
   - TTS audio generation

### Key Files to Reference

**Models**:
- `virtual_tutor/app_backend/app/models/admin.py` - Admin model with bcrypt
- `virtual_tutor/app_backend/app/models/tutor.py` - Tutor with admin_id FK
- `virtual_tutor/app_backend/app/models/student.py` - Student with tutor_id FK
- `virtual_tutor/app_backend/app/models/session.py` - Session with engine fields
- `virtual_tutor/app_backend/app/models/chat_message.py` - Message with role

**Authentication**:
- `virtual_tutor/app_backend/app/api/deps.py` - OAuth2 dependency injection
- `virtual_tutor/app_backend/app/core/security.py` - JWT encode/decode, bcrypt
- `virtual_tutor/app_backend/app/api/routes_student_auth.py` - Student login

**Frontend**:
- `virtual_tutor/frontend/src/services/authService.js` - Login flows
- `virtual_tutor/frontend/src/services/chatService.js` - Session APIs
- `virtual_tutor/frontend/src/components/HomePage.js` - Student chat UI

### Integration Checklist

- [ ] Convert virtual_tutor models to Flask-SQLAlchemy
- [ ] Add Alembic migrations for new tables
- [ ] Implement admin/student dual authentication
- [ ] Create admin APIs for tutor/student management
- [ ] Create student APIs for session/message handling
- [ ] Connect session creation with Avatar Manager
- [ ] Update frontend to support multi-tenant login
- [ ] Add RAG scoping per tutor (separate knowledge bases)
- [ ] Implement audit logging for admin actions
- [ ] Add session cleanup and resource management

## Hardware Requirements

**Minimum** (1-2 concurrent avatars):
- CPU: Intel i5 / AMD Ryzen 5 (4+ cores)
- RAM: 16GB
- GPU: NVIDIA GTX 1660 Ti (6GB VRAM)

**Recommended** (10+ concurrent avatars):
- CPU: Intel i7 / AMD Ryzen 7 (8+ cores)
- RAM: 32GB
- GPU: NVIDIA RTX 3090/4090 (24GB VRAM)

**Production** (50+ concurrent users):
- CPU: Intel Xeon / AMD EPYC (16+ cores)
- RAM: 64GB
- GPU: 2x NVIDIA RTX A6000 (48GB VRAM each)

## Troubleshooting

**Service Health Checks**:
```bash
curl http://localhost:8203/api/health  # Backend
curl http://localhost:8611/health      # LLM
curl http://localhost:8602/health      # RAG

# Check if services are listening
lsof -i :3000   # Frontend
lsof -i :8203   # Backend
lsof -i :8611   # LLM
lsof -i :8602   # RAG
lsof -i :8604   # TTS
lsof -i :8615   # Lip-Sync
```

**Common Issues**:

1. **"Service unavailable"** → Check all services are running (backend, llm, rag, tts, lip-sync)
2. **WebRTC connection fails** → Verify lip-sync service is running on port 8615+
3. **RAG returns no results** → Wait 2-3s after upload, check Milvus service
4. **Slow LLM responses** → Check GPU availability: `nvidia-smi`
5. **Avatar not displaying** → Ensure MuseTalk models are downloaded and lip-sync service started
6. **Conda environment errors** → Activate correct environment for each module

**Performance Benchmarks**:
- LLM TTFT: <1s (excellent), 1-3s (acceptable), >3s (investigate Ollama/GPU)
- Lip-sync FPS: >20 fps (good), <15 fps (check GPU load)

## Important File Paths

**Entry Points**:
- Backend: `backend/app.py` (Flask application factory), `backend/run.py` (dev server)
- Frontend: `frontend/src/App.js`
- LLM Service: `llm/api_interface_optimized.py`
- RAG Service: `rag/app.py`
- Lip-Sync Service: `lip-sync/app.py` (main), `lip-sync/live_server.py` (avatar server)
- TTS Service: `tts/tts.py` (main interface)

**Configuration**:
- Backend Config: `backend/config.py`
- Frontend Config: `frontend/src/config.js`
- Lip-Sync Config: `lip-sync/lip-sync.json`
- TTS Config: `tts/config.json`, `tts/model_info.json`

**Documentation**:
- Main README: `README.md`
- Test README: `test/README.md`
- Module READMEs: `{module}/README.md`

## Team & License

**Team**: UNSW CSE COMP9900 - Team H15A_BREAD

**License**: Educational use only (UNSW coursework)

**Last Updated**: November 2025
