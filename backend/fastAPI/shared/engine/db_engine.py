"""FastAPI lifespan handler for database initialisation and teardown.

Initialises MongoDB (via Beanie) and PostgreSQL (via SQLModel/SQLAlchemy)
on application startup and closes the PostgreSQL connection on shutdown.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .postgres import close_postgres, init_postgres
from .mongo import init_mongo


@asynccontextmanager
async def int_db_engine(app: FastAPI):

    postgres_initialized = False

    session_factory = await init_postgres()
    await init_mongo()

    if session_factory:
        postgres_initialized = True

    try:
        print("Mongo initalize!!!\nPostgres initialized!!!")
        yield {"db_session_factory": session_factory}
    finally:
        if postgres_initialized:
            await close_postgres()
            print("Supabase postgrres connection closed!!!")
