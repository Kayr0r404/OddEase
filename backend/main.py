from fastapi import FastAPI

from shared.engine.db_engine import int_db_engine
from services.user.api.v1.routes.routes import router as user_router
from services.auth.api.v1.routes.routes import router as auth_router

app = FastAPI(description="test", lifespan=int_db_engine)

app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
