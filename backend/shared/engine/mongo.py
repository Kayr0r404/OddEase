from contextlib import asynccontextmanager

from beanie import init_beanie
from pymongo import AsyncMongoClient


from shared.confiq import settings
from shared.models.no_sql_models import User


async def init_mongo():
    client = AsyncMongoClient(settings.mongo_db_url)

    db = client[settings.mongo_db_name]

    await init_beanie(database=db, document_models=[User])
