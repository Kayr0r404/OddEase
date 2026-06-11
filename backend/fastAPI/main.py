"""FastAPI application entry point.

Initialises the FastAPI app with database engines and registers
the user and auth API routers under the /api/v1 prefix.
"""

from starlette.datastructures import MutableHeaders

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.engine.db_engine import int_db_engine
from shared.auth import CurrentUser

from services.user.api.v1.routes.routes import router as user_router
from services.auth.api.v1.routes.routes import router as auth_router

app = FastAPI(description="OddEase API", lifespan=int_db_engine)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
