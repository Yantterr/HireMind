from fastapi import APIRouter, Request

import src.controllers.users_controllers as users_controllers
import src.services.users_services as users_services
from src.dataclasses.users_dataclasses import UserDataclass
from src.engines.database_engine import SessionDep
from src.models.auth_models import UserModel
from src.schemas import UserSchema

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.get('/me', response_model=UserModel)
async def get_current_user(
    request: Request,
) -> UserDataclass:
    """Get current user by token from cookie."""
    user = request.state.user
    return user


@users_router.get('/', response_model=list[UserModel])
async def get_all_users(
    db: SessionDep,
) -> list[UserSchema]:
    """Get all users."""
    users = await users_services.get_users(db=db)

    return users


@users_router.get('/{user_id}', response_model=UserModel)
async def get_user(
    user_id: int,
    db: SessionDep,
) -> UserSchema:
    """Get user by id."""
    user = await users_controllers.get_user(db=db, user_id=user_id)

    return user


@users_router.delete('/{user_id}', response_model=UserModel)
async def delete_user(
    user_id: int,
    db: SessionDep,
) -> UserSchema:
    """Delete user by id."""
    user = await users_controllers.delete_user(db=db, user_id=user_id)

    return user
