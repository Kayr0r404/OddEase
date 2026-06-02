from fastapi import APIRouter

from ..endpoints import root

# from shared.route_guard import public_route

router = APIRouter(prefix="/root", tags=["root"])

router.add_api_route(
    "/",
    root.index,
    methods=["get"],
    # **public_route(throttle_scope="root.index"),
)
