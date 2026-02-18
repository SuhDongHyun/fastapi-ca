from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import settings

DB_HOST = "192.168.49.2"
DB_PORT = "30432"
DB_NAME = "fastapi_ca"
DB_USER = settings.db.username
DB_PASS = settings.db.password


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 죽은 커넥션이면 감지 후 재연결
    echo=True,  # SQL 로그 확인용
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session


class Base(DeclarativeBase):
    pass
