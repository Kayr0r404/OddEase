from datetime import datetime as dt, timedelta, timezone
from typing import Dict

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from .confiq import settings

# +++++++++++ Password Hashing ++++++++++++++++++++++++++++++++++++++++++++++

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password=password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# +++++++++++ Access Token ++++++++++++++++++++++++++++++++++++++++++++++


def create_access_token(data: Dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = dt.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def verify_access_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401UNAUTHORIZED,
            detail="Token Expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]


def try_get_user_id_from_access_token(token: str | None = None) -> str | None:
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWKError:
        return None


# +++++++++++ Refresh Token ++++++++++++++++++++++++++++++++++++++++++++++


def create_refresh_token(data: Dict) -> str:
    payload = data.copy()
    expire = dt.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload.update(
        {
            "exp": expire,
            "iat": int(dt.now(timezone.utc).timestamp()),
            "type": "refresh",
        }
    )
    return jwt.encode(
        payload,
        settings.refresh_token_key.get_secret_value(),
        settings.algorithm,
    )


def verify_refresh_token(refresh_token: str) -> str | None:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.refresh_token_key.get_secret_value(),
            algorithms=[settings.algoritm],
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if payload.get("type") != "refresh":
        return None

    return payload.get("sub") or None
