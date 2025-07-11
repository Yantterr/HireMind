from secrets import choice
from string import digits
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import src.services.auth as auth_service
import src.utils.auth as auth_utils
from src.dataclasses.auth import UserCreateDataclass, UserDataclass, UserLoginDataclass
from src.logger import Logger
from src.models.generally import SystemRoleEnum
from src.models.user import UserCreateModel, UserLoginModel
from src.redis import AsyncRedis
from src.schemas import UserSchema


async def create_user(
    user_create_data: UserCreateModel, token: Optional[str], user_agent: str, db: AsyncSession, redis: AsyncRedis
) -> UserCreateDataclass:
    """Create a new user."""
    hashed_password = auth_utils.get_password_hash(user_create_data.password)

    if await auth_service.get_user_by_email(db=db, email=user_create_data.email):
        raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

    if token:
        user = auth_utils.decode_token(token=token)
        if user.role != SystemRoleEnum.ANONYM:
            raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

        user = await auth_service.edit_user(
            db=db,
            user_id=user.id,
            role=SystemRoleEnum.USER,
            username=user_create_data.username,
            email=user_create_data.email,
            password=hashed_password,
        )
    else:
        user = await auth_service.create_user(
            db=db,
            password=hashed_password,
            username=user_create_data.username,
            email=user_create_data.email,
            role=SystemRoleEnum.USER,
        )

    key = ''.join(choice(digits) for _ in range(6))
    await redis.set(name=f'{user.id}/key/{user_agent}', value=key, expire=900)

    new_token = auth_utils.get_token(user=UserDataclass.from_orm(user))
    await redis.set(name=f'{user.id}/agent:{user_agent}', value=new_token, expire=2_592_000)

    return UserCreateDataclass(
        user=UserDataclass.from_orm(user),
        token=new_token,
        key=int(key),
    )


async def login_user(
    login_data: UserLoginModel, user_agent: str, db: AsyncSession, redis: AsyncRedis
) -> UserLoginDataclass:
    """Login user."""
    user = await auth_service.get_user_by_email(db=db, email=login_data.email)
    if not user:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    if user.role == 'anonym' or not user.password or not user.username:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    password_correct = auth_utils.verify_password(login_data.password, user.password)
    if not password_correct:
        raise Logger.create_response_error(error_key='password_not_correct', is_cookie_remove=False)

    token = auth_utils.get_token(user=UserDataclass.from_orm(user))
    await redis.set(name=f'{user.id}/agent:{user_agent}', value=token, expire=2_592_000)

    return UserLoginDataclass(token=token, user=UserDataclass.from_orm(user))


async def logout_user(user_id: int, user_agent: str, redis: AsyncRedis) -> str:
    """Logout user."""
    await redis.delete(f'{user_id}/agent:{user_agent}')

    return 'User was logged out successfully.'


async def refresh_token(user: UserDataclass, user_agent: str, redis: AsyncRedis) -> str:
    """Refresh JWT token and update cookie."""
    new_token = auth_utils.get_token(user=user)

    await redis.set(name=f'{user.id}/agent:{user_agent}', value=new_token, expire=2_592_000)

    return new_token


async def confirm_email(
    user_id: int, user_agent: str, key: int, redis: AsyncRedis, db: AsyncSession
) -> UserLoginDataclass:
    """Confirm email."""
    redis_key = await redis.get(f'{user_id}/key/{user_agent}')

    if redis_key is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    if int(redis_key) != key:
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    updated_user = await auth_service.edit_user(db=db, user_id=user_id, is_activated=True)
    updated_user_dataclass = UserDataclass.from_orm(updated_user)

    await redis.delete(f'{user_id}/key/{user_agent}')

    new_token = auth_utils.get_token(user=updated_user_dataclass)
    await redis.set(name=f'{user_id}/agent:{user_agent}', value=new_token, expire=2_592_000)

    return UserLoginDataclass(token=new_token, user=updated_user_dataclass)
