"""PostgreSQL table models (SQLModel).

Defines Image, Comment, and Like tables created in PostgreSQL
via SQLModel.metadata.create_all.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Image(BaseModel, table=True):
    image_url: str = Field(nullable=False, unique=True)


class Comment(BaseModel, table=True):
    content: str


class Like(BaseModel, table=True):
    user_id: UUID
