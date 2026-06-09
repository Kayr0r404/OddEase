from fastapi import APIRouter, status

from ..endpoints import endpoints
from shared.route_guard import protected_route, public_route
from ....schemas.user_schema import PrivateUser, PublicUser

router = APIRouter(prefix="/users", tags=["User Managemnt"])
router.add_api_route(
    "/",
    endpoints.get_users,
    methods=["GET"],
    status_code=status.HTTP_200_OK,
    response_model=PublicUser,
    **public_route(throttle_scope="users.get_all_users"),
)

router.add_api_route(
    "/{user_id}",
    endpoints.get_user_by_id,
    methods=["GET"],
    status_code=status.HTTP_200_OK,
    response_model=PublicUser,
    **public_route(throttle_scope="users.get_user_by_id"),
)

router.add_api_route(
    "/register-new-account",
    endpoints.create_user,
    methods=["Post"],
    status_code=status.HTTP_201_CREATED,
    response_model=PrivateUser,
    **public_route(throttle_scope="users.create_new_account"),
)


router.add_api_route(
    "/update/{user_id}",
    endpoints.update_user,
    methods=["PUT"],
    status_code=status.HTTP_200_OK,
    response_model=PrivateUser,
    **public_route(throttle_scope="users.update_user"),
)


router.add_api_route(
    "/delete/{user_id}",
    endpoints.delete_user,
    methods=["DELETE"],
    status_code=status.HTTP_200_OK,
    **public_route(throttle_scope="users.delete_user"),
)
