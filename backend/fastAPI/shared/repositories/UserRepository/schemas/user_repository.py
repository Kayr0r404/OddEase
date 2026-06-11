"""User repository data transfer objects and protocol.

Defines PrivateUserRecord (includes hashed_password),
PublicUserRecord (excludes sensitive data), and the
UserRepository protocol interface.
"""

from pydantic import BaseModel, EmailStr
from typing import Any, List, Literal, Protocol


class PrivateUserRecord(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    username: str
    avatar_url: str | None = None
    sex: Literal["Male", "Female"]


class PublicUserRecord(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    avatar_url: str | None = None
    sex: Literal["Male", "Female"]


class UserRepository(Protocol):
    async def get_by_email(self, email: EmailStr) -> PrivateUserRecord | None: ...

    async def get_by_id(self, user_id: str) -> PublicUserRecord | None: ...

    async def update_user(
        self, user_id: str, data: dict[str, Any]
    ) -> PrivateUserRecord | None: ...
    async def delete_user(self, user_id: str) -> bool: ...
    async def create_user(self, data: dict) -> PrivateUserRecord: ...
    async def get_users(self) -> List[PublicUserRecord]: ...
