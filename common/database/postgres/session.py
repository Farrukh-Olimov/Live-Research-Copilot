from typing import Optional, AsyncGenerator
import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

_async_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def init_database():
    global _async_engine
    global _async_session_factory

    if _async_engine is None:
        ASYNC_DATABASE_URL = (
            "postgresql+asyncpg://"
            f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
            f"/{os.getenv('POSTGRES_DATABASE')}"
        )

        _async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
            max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", 5)),
            pool_size=int(os.getenv("POSTGRES_POOL_SIZE", 10)),
            pool_timeout=int(os.getenv("POSTGRES_POOL_TIMEOUT", 60)),
            pool_recycle=int(os.getenv("POSTGRES_POOL_RECYCLE", 3600)),
        )

    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            _async_engine, expire_on_commit=False
        )


async def get_session() -> AsyncGenerator:
    if _async_session_factory is None:
        raise RuntimeError("Call init_database() first")

    async with _async_session_factory() as session:
        yield session


async def cleanup():
    """Call on app shutdown."""
    global _async_engine
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
