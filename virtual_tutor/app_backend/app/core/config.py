import os
from functools import lru_cache

from dotenv import load_dotenv

# 自动从 .env 文件加载环境变量
load_dotenv()


class Settings:
    PROJECT_NAME: str = "Virtual Tutor System"

    # JWT / 安全相关
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # 数据库连接
    SQLALCHEMY_DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./dev.db"
    )

     # 初始 Admin（开发用）
    INIT_ADMIN_EMAIL: str = os.getenv("INIT_ADMIN_EMAIL", "admin@example.com")
    INIT_ADMIN_PASSWORD: str = os.getenv("INIT_ADMIN_PASSWORD", "admin123")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
