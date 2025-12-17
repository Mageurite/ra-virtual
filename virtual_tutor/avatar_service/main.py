"""
Avatar AI Engine - Serverless Service
独立的 AI 推理服务（无数据库依赖）
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from llm.routes import router as llm_router
from avatar.routes import router as avatar_router
from tts.routes import router as tts_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Avatar AI Engine",
        description="Serverless AI Inference Service for LLM and Avatar",
        version="1.0.0"
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Serverless 环境通常允许所有来源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health_check():
        """健康检查"""
        return {
            "status": "ok",
            "service": "avatar-ai-engine",
            "version": "1.0.0"
        }

    @app.get("/")
    def root():
        """服务信息"""
        return {
            "service": "Avatar AI Engine",
            "description": "Serverless AI Inference Service",
            "endpoints": {
                "llm": "/api/chat/*",
                "avatar": "/api/avatar/*",
                "tts": "/api/tts/*",
                "docs": "/docs",
                "health": "/health"
            }
        }

    # 注册路由 - 只包含 AI 推理相关的端点
    app.include_router(llm_router, prefix="/api/chat", tags=["LLM"])
    app.include_router(tts_router, prefix="/api/tts", tags=["TTS"])
    app.include_router(avatar_router, prefix="/api/avatar", tags=["Avatar"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
