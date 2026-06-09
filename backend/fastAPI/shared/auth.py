from datetime import datetime as dt, timedelta, timezone
from typing import Annotated, Dict, Optional

import jwt
from beanie import PydanticObjectId
from fastapi import Cookie, Depends, HTTPException, Request, status
from pwdlib import PasswordHash

from .confiq import settings
from .models.no_sql_models import User
from .repositories.UserRepository.schemas.user_repository import PrivateUserRecord

# +++++++++++ Password Hashing ++++++++++++++++++++++++++++++++++++++++++++++

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password=password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# +++++++++++ Access Token ++++++++++++++++++++++++++++++++++++++++++++++

import uuid
import jwt

# from datetime import datetime as dt, timedelta, timezone
# from typing import Dict


def create_access_token(data: Dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    expire = dt.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": dt.now(timezone.utc),  # issued-at for auditing
            "jti": str(uuid.uuid4()),  # unique ID for revocation support
            "type": "access",  # reject refresh tokens used as access
        }
    )

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
        settings.refresh_key.get_secret_value(),
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


# +++++++++++ Current User ++++++++++++++++++++++++++++++++++++++++++++++


async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),  # or Cookie(None)
    csrf_token: Optional[str] = Cookie(None),
) -> PrivateUserRecord:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},  # fixed header name
        )

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        header_csrf = request.headers.get("X-CSRF-Token")
        if not header_csrf or header_csrf != csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF validation failed.",
            )

    user_id = verify_access_token(token=access_token)
    if not user_id:  # check the result, not the token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        object_id = PydanticObjectId(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await User.get(object_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )
    return user


CurrentUser = Annotated[
    PrivateUserRecord, Depends(get_current_user)
]  # aligned with return type
