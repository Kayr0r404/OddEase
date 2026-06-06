from fastapi import APIRouter, status

from ..endpoints import endpoints

router = APIRouter(prefix="/auth", tags=["Authenticatioon"])

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
