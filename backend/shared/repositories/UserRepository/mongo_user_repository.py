from typing import Any, Dict, List

from pydantic import EmailStr

from shared.models.no_sql_models import User
from .schemas.user_repository import PrivateUserRecord, PublicUserRecord


class MongoUserRepository:

    @staticmethod
    def _to_public_reciord(user: User) -> PublicUserRecord:
        return PublicUserRecord(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            username=user.username,
            sex=user.sex,
            created_at=user.created_at,
        )

    @staticmethod
    def _to_private_reciord(user: User) -> PrivateUserRecord:
        return PublicUserRecord(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            username=user.username,
            sex=user.sex,
            created_at=user.created_at,
        )

    async def get_by_email(self, email: EmailStr) -> PrivateUserRecord | None:
        user = await User.find_one(email.lower() == User.email.lower())
        return self._to_private_reciord(user) if user else None

    async def get_by_id(self, user_id: str) -> PublicUserRecord | None:
        user = await User.find_one(User.id == user_id)

        return self._to_public_reciord(user) if user else None

    async def update_user(self, user_id: str, data: Dict[str, Any]): ...
    async def delete_user(self, user_id: str): ...
    async def create_user(self, user: Dict[str, Any]):
        user = User(
            first_name=user["first_name"].capitalize(),
            last_name=user["last_name"].capitalize(),
            email=user["email"].lower(),
            sex=user["sex"].capitalize(),
            username=user["username"].lower(),
            hashed_password=user["hashed_password"],
        )

        await user.insert()
        return self._to_private_reciord(user)

    async def get_users(self) -> List[PublicUserRecord]: ...
