from shared.confiq import settings


async def init_mongo():
    mongo_url = settings.mongo_url
