"""Application settings loaded from environment variables.

Uses pydantic-settings to read a .env file and validate configuration
for JWT tokens, PostgreSQL, and MongoDB connections.
"""

import os
from typing import Annotated

from pydantic import computed_field, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

base_dir = os.path.dirname(os.path.abspath(__file__))
fastapi_root_dir = os.path.abspath(os.path.join(base_dir, ".."))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(fastapi_root_dir, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: SecretStr
    refresh_key: SecretStr

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10
    refresh_token_expire_days: int = 7

    postgres_db_name: str
    postgres_db_host: str
    postgres_db_port: Annotated[int, Field(ge=1, le=65000)]
    postgres_db_user: str
    postgres_db_password: str

    mongo_db_name: str
    mongo_db_host: str
    mongo_db_port: Annotated[int, Field(ge=1, le=65000)]
    mongo_db_user: str
    mongo_db_password: str

    user_db_provider: str = "mongo"

    @computed_field
    @property
    def postgres_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_db_user}:{self.postgres_db_password}"
            f"@{self.postgres_db_host}:{self.postgres_db_port}/{self.postgres_db_name}"
        )

    @computed_field
    @property
    def mongo_db_url(self) -> str:
        return (
            f"mongodb://"
            # f"{self.mongo_db_user}:{self.mongo_db_password}"
            f"{self.mongo_db_host}:{self.mongo_db_port}"
        )


settings = Settings()
