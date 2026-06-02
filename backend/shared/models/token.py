from pydantic import BaseModel


class Token(BaseModel):
    access_toke: str
    token_type: str
