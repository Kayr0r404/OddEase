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

    db_name: str
    db_host: str
    db_port: Annotated[int, Field(ge=1, le=65000)]
    db_user: str
    db_password: str

    @computed_field
    @property
    def postgres_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
