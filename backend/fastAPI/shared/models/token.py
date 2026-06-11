"""Pydantic model for JWT token responses."""

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
