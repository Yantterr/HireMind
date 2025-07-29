from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

import src.controllers.users_controllers as users_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.services.users_services as users_services
import src.utils.auth_utils as auth_utils
from src.config import settings
from src.dataclasses.users_dataclasses import UserDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger
from src.models.auth_models import UserConfirmEmailModel, UserModel
from src.schemas import UserSchema

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.get('/me', response_model=UserModel)
async def get_current_user(
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('anonym'))],
) -> UserDataclass:
    """Get current user by token from cookie."""
    return user


@users_router.patch('/confirm_email', response_model=UserModel)
async def confirm_email(
    request: Request,
    response: Response,
    confirm_email_data: UserConfirmEmailModel,
    db: SessionDep,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> UserDataclass:
    """Confirm email by access key."""
    auth_info = auth_utils.get_validated_auth_info(request)
    if auth_info.error:
        raise Logger.create_response_error(error_key=auth_info.error, is_cookie_remove=False)

    result = await users_controllers.confirm_email(
        user_id=user.id, user_agent=auth_info.user_agent, key=confirm_email_data.key, db=db, redis=redis
    )

    response.set_cookie(value=result.token, **settings.auth_token_config)
    return result.user


@users_router.get('/', response_model=list[UserModel])
async def get_all_users(db: SessionDep, request: Request) -> list[UserSchema]:
    """Get list of users."""
    await auth_dependencies.require_permission('admin')(request=request)
    users = await users_services.get_users(db=db)

    return users


@users_router.get('/{user_id}', response_model=UserModel)
async def get_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Get user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.get_user(db=db, user_id=user_id)

    return user


@users_router.delete('/{user_id}', response_model=UserModel)
async def delete_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Delete user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.delete_user(db=db, user_id=user_id)

    return user
