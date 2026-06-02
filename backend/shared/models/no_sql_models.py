from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import IndexModel


class User(Document):
    id: UUID = Field(default_factory=uuid4)

    user_name: str
    avatar_url: str | None = None

    first_name: str
    last_name: str

    email: EmailStr
    hashed_password: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = [
            IndexModel("user_name", unique=True),
            IndexModel("email", unique=True),
        ]


class Review(Document):
    user_id: UUID
    rating: int
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reviews"
