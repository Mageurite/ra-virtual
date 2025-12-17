from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _get_connect_args(database_url: str):
    # SQLite 需要这个参数允许多线程访问
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args=_get_connect_args(settings.SQLALCHEMY_DATABASE_URL),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI 依赖，用于获取数据库 session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
