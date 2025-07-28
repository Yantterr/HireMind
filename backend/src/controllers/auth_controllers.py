from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import src.services.auth_services as auth_service
import src.services.users_services as users_service
import src.utils.auth_utils as auth_utils
from src.config import settings
from src.dataclasses.auth_dataclasses import AuthLoginDataclass, AuthRegisterDataclass
from src.dataclasses.users_dataclasses import UserDataclass
from src.engines.redis_engine import AsyncRedis
from src.logger import Logger
from src.models.auth_models import UserCreateModel, UserLoginModel
from src.models.generally_models import SystemRoleEnum


async def create_user(
    user_create_data: UserCreateModel,
    token: Optional[str],
    user_agent: str,
    db: AsyncSession,
    redis: AsyncRedis,
) -> AuthRegisterDataclass:
    """Create a new user."""
    if await users_service.get_user_by_email(
        db=db, email=user_create_data.email
    ) or await users_service.get_user_by_username(db=db, username=user_create_data.username):
        raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

    hashed_password = auth_utils.get_password_hash(user_create_data.password)
    if token:
        user_dataclass_old, _ = auth_utils.token_expire_verify(token=token)
        if user_dataclass_old.role != SystemRoleEnum.ANONYM:
            raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

        user_orm = await users_service.edit_user(
            db=db,
            user_id=user_dataclass_old.id,
            role=SystemRoleEnum.USER,
            username=user_create_data.username,
            email=user_create_data.email,
            password=hashed_password,
        )

    else:
        user_orm = await auth_service.create_user(
            db=db,
            password=hashed_password,
            username=user_create_data.username,
            email=user_create_data.email,
            role=SystemRoleEnum.ADMIN,
        )

    user_dataclass = UserDataclass.from_orm(user_orm)
    key = auth_utils.email_key_generate()
    await redis.set(name=f'{user_dataclass.id}/key/{user_agent}', value=str(key), expire=900)

    new_token = auth_utils.token_generate(user=user_dataclass)
    await redis.set(
        name=f'{user_dataclass.id}/agent:{user_agent}', value=new_token, expire=settings.redis_token_time_live
    )

    return AuthRegisterDataclass(
        user=user_dataclass,
        token=new_token,
        key=key,
    )


async def login_user(
    login_data: UserLoginModel, user_agent: str, db: AsyncSession, redis: AsyncRedis
) -> AuthLoginDataclass:
    """Login user."""
    user_orm = await users_service.get_user_by_email(db=db, email=login_data.email)
    if not user_orm:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    if user_orm.role == 'anonym' or not user_orm.password or not user_orm.username:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    password_correct = auth_utils.verify_password(login_data.password, user_orm.password)
    if not password_correct:
        raise Logger.create_response_error(error_key='password_not_correct', is_cookie_remove=False)

    user_dataclass = UserDataclass.from_orm(user_orm)

    token = auth_utils.token_generate(user=user_dataclass)
    await redis.set(name=f'{user_dataclass.id}/agent:{user_agent}', value=token, expire=settings.redis_token_time_live)

    return AuthLoginDataclass(token=token, user=user_dataclass)


async def logout_user(user_id: int, user_agent: str, redis: AsyncRedis) -> str:
    """Logout user."""
    await redis.delete(f'{user_id}/agent:{user_agent}')

    return 'User was logged out successfully.'


async def refresh_token(user: UserDataclass, user_agent: str, redis: AsyncRedis) -> str:
    """Refresh JWT token and update cookie."""
    new_token = auth_utils.token_generate(user=user)

    await redis.set(name=f'{user.id}/agent:{user_agent}', value=new_token, expire=settings.redis_token_time_live)

    return new_token


async def email_new_key(user_id: int, user_agent: str, redis: AsyncRedis) -> int:
    """Generate new key for email confirmation."""
    if await redis.get(f'{user_id}/key/{user_agent}'):
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    new_key = auth_utils.email_key_generate()
    await redis.set(name=f'{user_id}/key/{user_agent}', value=str(new_key), expire=900)

    return new_key


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
