"""MongoDB connection initialisation via Beanie ODM.

Creates an async MongoDB client and initialises Beanie with the
User document model.
"""

from beanie import init_beanie
from pymongo import AsyncMongoClient


from shared.confiq import settings
from shared.models.no_sql_models import User


async def init_mongo():
    client = AsyncMongoClient(settings.mongo_db_url)

    db = client[settings.mongo_db_name]

    await init_beanie(database=db, document_models=[User])
