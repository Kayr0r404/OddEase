"""User endpoint handlers: CRUD operations for user accounts.

Provides create, read, update, delete, and list operations for users,
with authorisation checks and duplicate-email validation.
"""

from typing import Annotated, Any, List

from fastapi import Depends, HTTPException, Request, status

from ....schemas.user_schema import CreateUser, PrivateUser, PublicUser
from shared.repositories.factory import get_user_repository
from shared.repositories.UserRepository.mongo_user_repository import MongoUserRepository
from shared.auth import CurrentUser


async def create_user(
    data: CreateUser,
    user_repo: MongoUserRepository = Depends(get_user_repository),
) -> PrivateUser:

    existing = await user_repo.get_by_email(email=data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = await user_repo.create_user(data.model_dump())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user.",
        )
    return user


async def update_user(
    user_id: str,
    data: PrivateUser,
    user_repo: MongoUserRepository = Depends(get_user_repository),
    current_user_id: Annotated[str, Depends(CurrentUser)] = None,
) -> PrivateUser:
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to complete this operation",
        )

    existing = await user_repo.get_by_id(user_id=user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    updated = await user_repo.update_user(
        user_id=user_id, data=data.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user.",
        )
    return updated


async def delete_user(
    user_id: str,
    user_repo: MongoUserRepository = Depends(get_user_repository),
    current_user_id: Annotated[str, Depends(CurrentUser)] = None,
) -> bool:
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.status.HTTP_401_NOT_AUTHORIZED,
            detail="Not authorized to complete this operation",
        )

    existing = await user_repo.get_by_id(user_id=user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    deleted = await user_repo.delete_user(user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user.",
        )
    return True


async def get_user_by_id(
    user_id: str,
    user_repo: MongoUserRepository = Depends(get_user_repository),
) -> PublicUser:

    user = await user_repo.get_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user


async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    user_repo: MongoUserRepository = Depends(get_user_repository),
) -> List[PublicUser]:
    print(request.headers)
    try:
        users_data = await user_repo.get_all(skip=skip, limit=limit).to_list()
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to fetch users"
        )

    return [PublicUser.model_validate(u) for u in users_data]
