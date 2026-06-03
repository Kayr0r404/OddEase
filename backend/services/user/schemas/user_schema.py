from typing import Literal

from pydantic import BaseModel, EmailStr


class PrivateUser(BaseModel):
    id: str
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    user_name: str
    avatar_url: str | None = None
    sex: Literal["male", "female"]


class PublicUser(BaseModel):
    id: str
    first_name: str
    last_name: str
    user_name: str
    avatar_url: str | None = None
    sex: Literal["male", "female"]
