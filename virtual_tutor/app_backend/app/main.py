from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import Base, engine
from app import models  # noqa: F401
from app.api.routes_auth import router as auth_router
from app.api.routes_tutors import router as tutors_router
from app.api.routes_student_admin import router as admin_students_router
from app.api.routes_student_auth import router as student_auth_router
from app.api.routes_sessions import router as student_sessions_router
from app.api.routes_avatar_admin import router as avatar_admin_router
from app.api.routes_avatar_public import router as avatar_public_router

def create_app() -> FastAPI:
    # 创建表（开发环境）
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title=settings.PROJECT_NAME)

    # CORS 配置 - 允许前端访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://51.161.130.234:3000",
            "http://localhost:3000",
            "http://localhost:8080",  # Avatar Frontend
            "http://127.0.0.1:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    # 注册路由
    app.include_router(auth_router)
    app.include_router(tutors_router)
    app.include_router(admin_students_router)
    app.include_router(student_auth_router)
    app.include_router(student_sessions_router)
    
    # Avatar 相关路由（代理到 Avatar Service）
    app.include_router(avatar_admin_router)   # 管理员管理 Avatar
    app.include_router(avatar_public_router)  # 学生访问 Avatar

    return app


app = create_app()
