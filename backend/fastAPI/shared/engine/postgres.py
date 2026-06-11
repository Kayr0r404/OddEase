"""PostgreSQL connection initialisation via SQLModel/SQLAlchemy.

Creates an async SQLAlchemy engine with asyncpg, runs DDL to create
all tables, and provides a session factory for dependency injection.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from shared.confiq import settings
from shared.models.sql_models import *

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


async def init_postgres():
    global engine, SessionLocal

    if not settings.postgres_db_url:
        raise ValueError("POSTGRES DB URL is required for postgres based services.")

    if engine is None:
        engine = create_async_engine(
            settings.postgres_db_url,
            future=True,
            echo=False,
            connect_args={"statement_cache_size": 0},
        )

        SessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    return SessionLocal


def get_session():
    yield SessionLocal


async def close_postgres():
    global engine, SessionLocal

    if engine is not None:
        await engine.dispose()
        engine = None
        SessionLocal = None
