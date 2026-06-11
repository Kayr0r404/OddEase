"""User repository factory.

Returns the appropriate repository implementation (MongoDB or PostgreSQL)
based on the USER_DB_PROVIDER setting.
"""

from shared.confiq import settings
from shared.repositories.UserRepository.postgres_user_repository import (
    PostgresUserRepository,
)
from shared.repositories.UserRepository.mongo_user_repository import (
    MongoUserRepository,
)


def get_user_repository():
    backend = (settings.user_db_provider).lower()
    if backend == "mongo":
        return MongoUserRepository()
    if backend in {"supabase", "postgres"}:
        return PostgresUserRepository()
    raise ValueError(f"Unsupported USER_DB_PROVIDER '{backend.upper()}'")
