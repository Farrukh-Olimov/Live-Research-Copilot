import os
import asyncio
from dotenv import load_dotenv
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from common.database.postgres.models.base import BaseModel
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)

load_dotenv(".env")


def get_admin_url():
    return (
        "postgresql+asyncpg://"
        f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
        f"/postgres"
    )


def get_test_db_url():
    return (
        "postgresql+asyncpg://"
        f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
        f"/{os.getenv('POSTGRES_DATABASE_TEST')}"
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_database():
    database = os.getenv("POSTGRES_DATABASE_TEST")
    admin_engine = create_async_engine(url=get_admin_url(), isolation_level="AUTOCOMMIT")

    # Create test DB if not exists
    async with admin_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database"),
            {"database": database},
        )
        exists = result.scalar_one_or_none()

        if exists is None:
            await conn.execute(text(f"CREATE DATABASE {database}"))
            logger.info(f"Database {database} created")
        else:
            logger.info(f"Database {database} already exists")

    # Create tables
    engine = create_async_engine(get_test_db_url())
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    await engine.dispose()

    yield

    # Drop tables then terminate connections then drop DB
    engine = create_async_engine(get_test_db_url())
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()

    async with admin_engine.connect() as conn:
        # Terminate all connections to test DB before dropping
        await conn.execute(
            text("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = :database AND pid <> pg_backend_pid()
            """),
            {"database": database},
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {database}"))
        logger.info(f"Database {database} dropped")

    await admin_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_engine(init_database):
    engine = create_async_engine(
        get_test_db_url(),
        max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", 5)),
        pool_size=int(os.getenv("POSTGRES_POOL_SIZE", 10)),
        pool_timeout=int(os.getenv("POSTGRES_POOL_TIMEOUT", 60)),
        pool_recycle=int(os.getenv("POSTGRES_POOL_RECYCLE", 3600)),
        echo=False,
    )
    yield engine
    await engine.dispose()  # disposes before init_database teardown


@pytest_asyncio.fixture(scope="function")
async def async_session_factory(async_engine):
    factory = async_sessionmaker(async_engine, expire_on_commit=False)
    yield factory

    # Clean up all data after each test
    async with factory() as session:
        await session.execute(
            text("""
                TRUNCATE TABLE
                    paper_ingestion_state,
                    paper_authors,
                    paper_subjects,
                    papers,
                    subjects,
                    domains,
                    authors
                RESTART IDENTITY CASCADE;
            """)
        )
        await session.commit()