from sqlalchemy.ext.asyncio import AsyncSession

import src.services.auth_services as auth_services
import src.services.users_services as users_service
import src.utils.auth_utils as auth_utils
from src.config import settings
from src.dataclasses.auth_dataclasses import AuthLoginDataclass
from src.dataclasses.users_dataclasses import UserDataclass
from src.engines.redis_engine import AsyncRedis
from src.logger import Logger
from src.schemas import UserSchema


async def get_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Controller for get user by id."""
    user = await users_service.get_user_by_id(db=db, user_id=user_id)

    if not user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)

    return user


async def delete_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Controller for delete user by id."""
    removed_user = await auth_services.delete_user(db=db, user_id=user_id)

    if not removed_user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)

    return removed_user


async def confirm_email(
    user_id: int, user_agent: str, key: int, redis: AsyncRedis, db: AsyncSession
) -> AuthLoginDataclass:
    """Confirm email."""
    redis_key = await redis.get(f'{user_id}/key/{user_agent}')

    if redis_key is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    if int(redis_key) != key:
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    updated_user = await users_service.edit_user(db=db, user_id=user_id, is_activated=True)
    updated_user_dataclass = UserDataclass.from_orm(updated_user)

    await redis.delete(f'{user_id}/key/{user_agent}')

    new_token = auth_utils.token_generate(user=updated_user_dataclass)
    await redis.set(name=f'{user_id}/agent:{user_agent}', value=new_token, expire=settings.redis_token_time_live)

    return AuthLoginDataclass(token=new_token, user=updated_user_dataclass)
