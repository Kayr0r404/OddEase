import asyncio
import time
from dataclasses import dataclass
from secrets import compare_digest
from typing import Any, Dict, Literal, Tuple

from fastapi import Cookie, Depends, HTTPException, Request, status

from shared.auth import verify_access_token
from shared.repositories.factory import get_user_repository

AUTHMODE = Literal["public", "protected"]
THROTTLEKEYMODE = Literal["ip", "user"]
ROUTETHROTTLE = Tuple[int, int]

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
DEFAULT_PUBLIC_LIMIT: ROUTETHROTTLE = (120, 120)
DEFAULT_PROTECTED_LIMIT: ROUTETHROTTLE = 60, 60


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


class InMemoryRateStore:
    def __init__(self) -> None:
        self._buckets: dict[str, tuple[float, int]] = {}
        self._lock = asyncio.Lock()

    async def hit(self, key: str, window_seconds: int) -> int:
        now = time.time()
        async with self._lock:
            window_start, count = self._buckets.get(key, (now, 0))
            if now - window_start >= window_seconds:
                window_start, count = now, 0
            count += 1
            self._buckets[key] = (window_start, count)
            return count


@dataclass(frozen=True)
class GuardConfig:
    auth: AUTHMODE
    throttle: ROUTETHROTTLE
    throttle_key: THROTTLEKEYMODE
    csrf_required: bool
    require_verified_email: bool
    enforce_team_creation_limit: bool
    scope: str


_memory_store = InMemoryRateStore()


def _route_extra(config: GuardConfig) -> Dict[str, Any]:
    return {
        "x-route-guard": {
            "auth": config.auth,
            "throttle": {
                "requests": config.throttle[0],
                "window_seconds": config.throttle[1],
                "key": config.throttle_key,
                "scope": config.scope,
            },
            "csrf_required": config.csrf_required,
            "require_verified_email": config.require_verified_email,
            "enforce_team_creation_limit": config.enforce_team_creation_limit,
        }
    }


async def _apply_throttle(request: Request, config: GuardConfig) -> None:
    if config.throttle[0] <= 0:
        return

    subject = _client_ip(request)
    if config.throttle_key == "user":
        subject = str(getattr(request.state, "user_id", "")) or subject

    key = f"throttle: {config.scope}:{request.method}:{request.url.path}:{subject}"
    count = await _memory_store.hit(key=key, window_seconds=config.throttle[1])

    if count > config.throttle[0]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for this route.",
            headers={"Retry-After": str(config.throttle[1])},
        )


def _guard_dependency(config: GuardConfig):
    async def dependency(
        request: Request,
        access_token: str | None = Cookie(default=None),
        csrf_token: str | None = Cookie(default=None),
    ):
        if config.auth == "protected":
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not Authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_id = verify_access_token(token=access_token)
            request.state.user_id = user_id

            if config.require_verified_email:
                repo = get_user_repository
                user = await repo.get_by_id(str(user_id))
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User no loger exists.",
                    )
                if not user.email_verified:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Verify your email to use this action/ feature.",
                    )

            if config.csrf_required and request.method not in SAFE_METHODS:
                csrf_header = request.headers.get("x-csrf-token")
                if (
                    not csrf_token
                    or not csrf_header
                    or not compare_digest(csrf_header, csrf_token)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="CSRF validation failed.",
                    )

        await _apply_throttle(request=request, config=config)

    return dependency


def public_route(
    *,
    rate_limit: ROUTETHROTTLE | None = None,
    throttle_scope: str = "public",
) -> Dict[str, Any]:
    config = GuardConfig(
        auth="public",
        throttle=rate_limit or DEFAULT_PUBLIC_LIMIT,
        throttle_key="ip",
        csrf_required=False,
        require_verified_email=False,
        enforce_team_creation_limit=False,
        scope=throttle_scope,
    )

    return {
        "dependencies": [Depends(_guard_dependency(config=config))],
        "openapi_extra": _route_extra(config),
    }


def protected_route(
    *,
    rate_limit: ROUTETHROTTLE | None = None,
    throttle_scope: str = "protected",
    throttle_key: THROTTLEKEYMODE = "user",
    csrf_required: bool = True,
    require_verified_email: bool = False,
    enforce_team_creation_limit: bool = False,
) -> Dict[str, Any]:
    config = GuardConfig(
        auth="protected",
        throttle=rate_limit or DEFAULT_PROTECTED_LIMIT,
        throttle_key=throttle_key,
        csrf_required=csrf_required,
        require_verified_email=require_verified_email,
        enforce_team_creation_limit=enforce_team_creation_limit,
        scope=throttle_scope,
    )

    return {
        "dependencies": [Depends(_guard_dependency(config=config))],
        "openapi_extra": _route_extra(config=config),
    }
