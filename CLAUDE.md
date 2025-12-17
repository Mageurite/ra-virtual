# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Overview

This workspace (`/Users/murphyxu/Code/ra/`) contains multiple repositories for the Virtual Tutor project:

```
/Users/murphyxu/Code/ra/
├── mageurite_virtual_tutor/     # Main codebase (Phase 2 - Complete system)
├── virtual_tutor/               # Reference codebase (Phase 1 - Multi-tenant backend)
└── CLAUDE.md                    # This file
```

## Project Goal

**Objective**: Develop a complete AI Virtual Tutor system based on the `mageurite_virtual_tutor` codebase, integrating multi-tenant architecture concepts from `virtual_tutor`.

## Working Directory Structure

### 1. `mageurite_virtual_tutor/` (Primary Codebase)

**Source**: https://github.com/Mageurite/virtual-tutor.git

**Purpose**: Main development repository containing the complete Phase 2 system

**Key Features**:
- Real-time digital avatars with MuseTalk lip-sync
- Streaming AI chat with RAG integration
- Multi-user concurrent support
- WebRTC video streaming
- Microservices architecture (Frontend, Backend, LLM, RAG, Avatar Manager, TTS, Lip-sync)

**Documentation**: See `mageurite_virtual_tutor/CLAUDE.md` for detailed architecture, commands, and development guide

### 2. `virtual_tutor/` (Reference Codebase)

**Source**: https://github.com/Summer0310/virtual_tutor.git (feat/backend-student-auth branch)

**Purpose**: Multi-tenant backend architecture with student authentication and session management

**Architecture Overview**:
- **Backend**: FastAPI + SQLAlchemy 2.0 + Alembic (app_backend/)
- **Frontend**: React 19 + Material-UI + React Router (frontend/)
- **Database**: SQLite (dev) → PostgreSQL (production ready)

**Core Features**:

1. **Multi-Tenant Data Model**:
   - Admin → Tutor (1:N) → Student (1:N) hierarchy
   - Session → ChatMessage (1:N) for conversation history
   - Tenant isolation at Tutor level

2. **Authentication & Authorization**:
   - Dual OAuth2 Password Bearer flows (Admin + Student)
   - JWT tokens with role-based access control (role: "admin" | "student")
   - Token includes subject (user_id) + role for fine-grained authorization
   - Separate OAuth2 schemes for admin and student endpoints

3. **Session Management**:
   - Student creates Session → Backend returns engine_url + engine_token
   - Session tracks: tutor_id, student_id, status, timestamps
   - ChatMessage stores Q&A pairs (role: student/assistant/system)
   - Prepared for AI Engine integration (currently mock data)

4. **API Structure**:
   ```
   /api/auth/login              # Admin login
   /api/tutors/*                # Admin: Tutor CRUD
   /api/tutors/{id}/students/*  # Admin: Student management per Tutor
   /api/student/auth/login      # Student login (OAuth2)
   /api/student/sessions        # Student: Create/list sessions
   /api/student/sessions/{id}/messages  # Student: Chat messages
   ```

5. **Frontend Architecture**:
   - Modern React SPA with Material-UI design system
   - Components: HomePage, AdminLayout, UserTable, ChatWindow, etc.
   - Services: authService, chatService, adminService, tokenService
   - JWT token management with auto-refresh and expiry handling
   - Proxy setup for backend communication (port 8000)

**Key Implementation Details**:

- **Security**: `passlib[bcrypt]` for password hashing, `python-jose` for JWT
- **Dependencies**: fastapi, uvicorn, sqlalchemy, alembic, pydantic, psycopg2-binary
- **CORS**: Configured for localhost:3000 and deployment server (51.161.130.234:3000)
- **Database Models**: 
  - Admin, Tutor, Student (hierarchy)
  - Session (conversation metadata)
  - ChatMessage (Q&A records)
- **Deployment Ready**: gunicorn config, conda environment (vt_app), systemd service setup

**Use Case**: Reference this codebase when implementing:
- Multi-tenant database models with SQLAlchemy 2.0
- Dual authentication flows (admin + student)
- Session and message tracking
- React frontend with Material-UI
- JWT-based API security patterns
- FastAPI dependency injection patterns

## Development Workflow

### Primary Development

**Always work in `mageurite_virtual_tutor/` directory**:

```bash
cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor

# See detailed commands in mageurite_virtual_tutor/CLAUDE.md
```

### Integration Tasks

When integrating multi-tenant features from `virtual_tutor/`:

1. **Study reference implementation**:
   ```bash
   cd /Users/murphyxu/Code/ra/virtual_tutor/app_backend
   # Review models, schemas, and auth logic
   ```

2. **Implement in main codebase**:
   ```bash
   cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor/backend
   # Apply concepts to Flask backend
   ```

3. **Key Integration Points**:

   **Backend (FastAPI → Flask)**:
   - Database models: `virtual_tutor/app_backend/app/models/` → `mageurite_virtual_tutor/backend/models/`
     - Admin, Tutor, Student hierarchy with ForeignKey constraints
     - Session model with engine_url/engine_token fields
     - ChatMessage model with session relationship
   
   - Auth schemas: `virtual_tutor/app_backend/app/schemas/` → `mageurite_virtual_tutor/backend/schemas/`
   
   - Security utilities: `virtual_tutor/app_backend/app/core/security.py` → `mageurite_virtual_tutor/backend/services/security.py`
     - JWT encoding/decoding with role claims
     - Password hashing with bcrypt
     - OAuth2 dependency injection pattern
   
   - API routes: `virtual_tutor/app_backend/app/api/routes_*.py` → `mageurite_virtual_tutor/backend/routes/`
     - Dual authentication endpoints (admin + student)
     - Session creation and message APIs
     - Dependency injection for current_user

   **Frontend (React)**:
   - Components: `virtual_tutor/frontend/src/components/` → Adapt for mageurite_virtual_tutor
     - AdminLayout: Tutor and student management UI
     - HomePage: Student chat interface
     - TokenExpiryModal: JWT expiry handling
   
   - Services: `virtual_tutor/frontend/src/services/` → API client patterns
     - authService: Login flows with token storage
     - chatService: Session and message APIs
     - tokenService: Token refresh and validation
   
   - Utilities: `virtual_tutor/frontend/src/utils/request.js` → HTTP interceptors
     - Axios interceptors for JWT attachment
     - Error handling and retry logic
     - Token expiry detection

4. **Database Migration Strategy**:
   ```bash
   # In virtual_tutor (FastAPI + Alembic)
   cd app_backend
   alembic revision --autogenerate -m "Add sessions and messages"
   alembic upgrade head
   
   # Apply similar schema to mageurite_virtual_tutor
   # (Adapt for Flask-Migrate if using Flask-SQLAlchemy)
   ```

5. **Testing Integration**:
   - Reference: `virtual_tutor/app_backend/tests/test_student_text_chat.py`
   - Test auth flows, session creation, message posting
   - Verify multi-tenant isolation (students can't access other tutors' data)

## Quick Reference

### Start the System

```bash
cd /Users/murphyxu/Code/ra/mageurite_virtual_tutor

# 1. Start Redis
redis-server &

# 2. Start all services (see mageurite_virtual_tutor/CLAUDE.md for details)
cd llm && gunicorn --config gunicorn_config.py "api_interface_optimized:app" &
cd rag && python app.py &
cd avatar-manager && python manager.py &
cd backend && gunicorn --config gunicorn_config.py "app:create_app()" &
cd frontend && npm start
```

### Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8203
- **API Documentation**: http://localhost:8203/api/health

### Test Credentials

- Email: `test@example.com`
- Password: `password123`

## Important Notes

1. **Always refer to `mageurite_virtual_tutor/CLAUDE.md`** for detailed architecture, API documentation, and development commands

2. **The `virtual_tutor/` directory is reference implementation** - sync from GitHub before studying:
   ```bash
   cd /Users/murphyxu/Code/ra/virtual_tutor
   git checkout feat/backend-student-auth
   git pull origin feat/backend-student-auth
   ```

3. **Integration strategy**: Study Phase 1 multi-tenant patterns, then implement adapted versions in Phase 2 codebase
   - Phase 1 (virtual_tutor): FastAPI backend with authentication + React frontend (完成)
   - Phase 2 (mageurite_virtual_tutor): Integrate multi-tenant auth with AI engine services

4. **Hardware requirements**: NVIDIA GPU with 24GB+ VRAM recommended for full functionality

5. **Current Status (Dec 2025)**:
   - ✅ `virtual_tutor`: Complete backend with admin/student auth, session management, React frontend
   - ⏳ `mageurite_virtual_tutor`: AI engine services running, needs integration with multi-tenant backend

## Next Steps

To start development:

1. Read `mageurite_virtual_tutor/CLAUDE.md` for comprehensive system documentation
2. Review `mageurite_virtual_tutor/README.md` for feature overview
3. Set up conda environments and dependencies (see installation guides in each module)
4. Start services and verify system health
5. Begin feature development or integration tasks

### Integration Roadmap

**Phase 1: Study Reference Implementation** ✅
- Review `virtual_tutor/app_backend/` FastAPI architecture
- Understand multi-tenant data model (Admin → Tutor → Student → Session → ChatMessage)
- Study dual authentication pattern (admin vs student OAuth2)
- Review React frontend structure and Material-UI components

**Phase 2: Backend Integration** (Next)
- Integrate multi-tenant models into `mageurite_virtual_tutor/backend/`
- Add admin/student authentication endpoints
- Connect session management with AI engine services
- Implement RAG-aware chat endpoints with tutor-specific knowledge bases

**Phase 3: Frontend Development**
- Adapt React components from `virtual_tutor/frontend/`
- Build admin portal for tutor/student management
- Create student chat UI with avatar integration
- Implement session history and message replay

**Phase 4: AI Engine Integration**
- Connect session creation API with actual AI engine (replace mock data)
- Integrate LLM service with tutor-specific system prompts
- Enable RAG retrieval scoped to tutor's knowledge base
- Add real-time WebRTC avatar streaming with MuseTalk

**Phase 5: Production Deployment**
- Set up PostgreSQL for multi-tenant data
- Configure nginx reverse proxy for all services
- Implement logging and monitoring (audit logs per tutor)
- Performance optimization and load testing

## Documentation Hierarchy

```
/Users/murphyxu/Code/ra/CLAUDE.md              # This file (workspace overview)
    ↓
mageurite_virtual_tutor/CLAUDE.md              # Main system documentation
    ↓
mageurite_virtual_tutor/README.md              # Feature guide
mageurite_virtual_tutor/{module}/README.md     # Module-specific docs
```
