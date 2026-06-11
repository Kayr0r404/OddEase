"""Auth API route definitions.

Registers /token, /refresh, and /logout endpoints under /auth.
"""

from fastapi import APIRouter, status

from ..endpoints import endpoints

router = APIRouter(prefix="/auth", tags=["Authentication"])

router.add_api_route(
    "/token",
    endpoints.login_for_access_token,
    status_code=status.HTTP_201_CREATED,
    methods=["POST"],
)

router.add_api_route(
    "/refresh",
    endpoints.refresh_token,
    methods=["Post"],
    status_code=status.HTTP_201_CREATED,
)

router.add_api_route(
    "/logout",
    endpoints.logout,
    status_code=status.HTTP_200_OK,
    methods=["DELETE"],
)
