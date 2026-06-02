from contextlib import asynccontextmanager

from fastapi import FastAPI

from .postgres import close_postgres, init_postgres


@asynccontextmanager
async def int_db_engine(app: FastAPI):

    postgres_initialized = False

    session_factory = await init_postgres()

    if session_factory:
        postgres_initialized = True

    try:
        yield {"db_session_factory": session_factory}
    finally:
        if postgres_initialized:
            await close_postgres()
            print("Supabase postgrres connection closed!!!")
