from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_HOST = "192.168.49.2"
DB_PORT = "30432"
DB_NAME = "fastapi_ca"
DB_USER = "admin"
DB_PASS = "admin"


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


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
