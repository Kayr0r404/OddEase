from typing import Any, Dict, List

from pydantic import EmailStr

from shared.models.no_sql_models import User
from .schemas.user_repository import PrivateUserRecord, PublicUserRecord
from shared.auth import hash_password


class MongoUserRepository:

    @staticmethod
    def _to_public_record(user: User) -> PublicUserRecord:
        return PublicUserRecord(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            username=user.username,
            sex=user.sex,
        )

    @staticmethod
    def _to_private_record(user: User) -> PrivateUserRecord:
        return PrivateUserRecord(
            id=str(user.id),
            email=user.email,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.avatar_url,
            username=user.username,
            sex=user.sex,
        )

    async def get_by_email(self, email: EmailStr) -> PrivateUserRecord | None:
        user = await User.find_one(User.email == email.lower())
        return self._to_private_record(user) if user else None

    async def get_by_id(self, user_id: str) -> PublicUserRecord | None:
        user = await User.find_one(User.id == user_id)

        return self._to_public_record(user) if user else None

    async def update_user(self, user_id: str, data: Dict[str, Any]): ...
    async def delete_user(self, user_id: str): ...
    async def create_user(self, user: Dict[str, Any]):
        user = User(
            first_name=user["first_name"].capitalize(),
            last_name=user["last_name"].capitalize(),
            email=user["email"].lower(),
            sex=user["sex"].capitalize(),
            username=user["username"].lower(),
            hashed_password=hash_password(user["password"]),
        )

        await user.insert()
        return self._to_private_reciord(user)

    async def get_users(self) -> List[PublicUserRecord]: ...
