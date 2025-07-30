from sqlalchemy.ext.asyncio import AsyncSession

import src.services.auth_services as auth_services
import src.services.users_services as users_service
import src.utils.auth_utils as auth_utils
from src.config import settings
from src.dataclasses.auth_dataclasses import AuthSessionDataclass
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
) -> AuthSessionDataclass:
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

    return AuthSessionDataclass(token=new_token, user=updated_user_dataclass)


async def email_new_key(user_id: int, user_agent: str, redis: AsyncRedis) -> int:
    """Generate new key for email confirmation."""
    if await redis.get(f'{user_id}/key/{user_agent}'):
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    new_key = auth_utils.email_key_generate()
    await redis.set(name=f'{user_id}/key/{user_agent}', value=str(new_key), expire=900)

    return new_key


async def forgot_password(user: UserDataclass, user_agent: str, redis: AsyncRedis) -> int:
    """Controller for forgot password."""
    key = auth_utils.email_key_generate()
    await redis.set(name=f'{user.id}/key/{user_agent}', value=str(key), expire=900)

    return key


async def reset_password(
    new_password: str, key: int, user: UserDataclass, user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> str:
    """Controller for reset password."""
    redis_key = await redis.get(f'{user.id}/key/{user_agent}')
    if redis_key != str(key):
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    await redis.delete(f'{user.id}/key/{user_agent}')
    hashed_password = auth_utils.get_password_hash(new_password)
    await users_service.edit_user(db=db, user_id=user.id, password=hashed_password)

    return 'Password was changed successfully.'


async def edit_password(user_id: int, new_password: str, db: AsyncSession) -> str:
    """Controller for change password based on old password."""
    old_password_db = await users_service.get_user_password(db=db, user_id=user_id)
    if not old_password_db or not old_password_db.password:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    if not auth_utils.verify_password(new_password, old_password_db.password):
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    new_hashed_password = auth_utils.get_password_hash(new_password)
    await users_service.edit_user(db=db, user_id=user_id, password=new_hashed_password)

    return 'Password was changed successfully.'


async def edit_email(
    key: int, user_agent: str, new_email: str, user_id: int, db: AsyncSession, redis: AsyncRedis
) -> AuthSessionDataclass:
    """Controller for change email based on access key."""
    redis_key = await redis.get(f'{user_id}/key/{user_agent}')

    if key != redis_key:
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    await redis.delete(f'{user_id}/key/{user_agent}')

    updated_user = await users_service.edit_user(db=db, user_id=user_id, email=new_email)
    updated_user_dataclass = UserDataclass.from_orm(updated_user)

    new_token = auth_utils.token_generate(user=updated_user_dataclass)
    await redis.set(name=f'{user_id}/agent:{user_agent}', value=new_token, expire=settings.redis_token_time_live)

    return AuthSessionDataclass(token=new_token, user=updated_user_dataclass)


async def edit_username(
    user_id: int, username: str, user_agent: str, db: AsyncSession, redis: AsyncRedis
) -> AuthSessionDataclass:
    """Controller for change username."""
    updated_user = await users_service.edit_user(db=db, user_id=user_id, username=username)
    updated_user_dataclass = UserDataclass.from_orm(updated_user)

    new_token = auth_utils.token_generate(user=updated_user_dataclass)
    await redis.set(name=f'{user_id}/agent:{user_agent}', value=new_token, expire=settings.redis_token_time_live)

    return AuthSessionDataclass(token=new_token, user=updated_user_dataclass)
