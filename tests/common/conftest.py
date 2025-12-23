import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from common.database.postgres.models.base import BaseModel

DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    """Yields an async sqlalchemy engine.

    The engine is yielded to the test, and then disposed of
    after the test is finished.
    """
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"uri": True},
    )
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(async_engine):
    """Yields an async sqlalchemy session.

    This fixture is scoped to the session, meaning it will only be invoked
    once per test session.
    """
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()
