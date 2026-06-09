from typing import Literal

from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    username: str
    avatar_url: str | None = None
    sex: Literal["Male", "Female"] | None = None


class PrivateUser(BaseModel):
    id: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    username: str
    avatar_url: str | None = None
    sex: Literal["Male", "Female"]


class PublicUser(BaseModel):
    id: str
    first_name: str
    last_name: str
    username: str
    avatar_url: str | None = None
    sex: Literal["Male", "Female"]
