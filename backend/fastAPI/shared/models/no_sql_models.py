from datetime import datetime, timezone
from typing import Annotated, Literal

from beanie import Document, Indexed, Link
from pydantic import EmailStr, Field, field_validator
from pymongo import IndexModel


class User(Document):

    username: Annotated[str, Indexed(unique=True)]
    avatar_url: str | None = None

    first_name: str = Field(min_length=1, max_length=64)
    last_name: str = Field(min_length=1, max_length=64)

    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str

    sex: Literal["Male", "Female"]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("email", mode="before")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("username", mode="before")
    @classmethod
    def normalise_username(cls, v: str) -> str:
        return v.lower().strip()

    class Settings:
        name = "users"


class Review(Document):
    user: Link[User]
    rating: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reviews"
        indexes = [
            IndexModel("user.$id"),  # efficient lookups by user
        ]
