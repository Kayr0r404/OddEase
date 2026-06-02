from fastapi import FastAPI

from shared.engine.db_engine import int_db_engine
from appi.v1.routes.routes import router as index_routes

app = FastAPI(description="test", lifespan=int_db_engine)

app.include_router(index_routes, prefix="/api/v1")
