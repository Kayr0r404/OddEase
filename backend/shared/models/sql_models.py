from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class User(SQLModel, table=True):

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user_name: str = Field(nullable=False, unique=True)

    first_name: str
    last_name: str

    email: EmailStr = Field(nullable=False, unique=True)

    hashed_password: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Image(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    image_url: str = Field(nullable=False, unique=True)


class Reiew(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class Comment(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class Like(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
