from sqlalchemy.ext.asyncio import AsyncSession

import src.users.service as users_service
import src.users.utils as users_utils
from src.database import AsyncRedis
from src.logger import Logger
from src.users.models import create_user_result, user_create_model, user_login_model
from src.users.schemas import UserSchema


async def get_users(db: AsyncSession) -> list[UserSchema]:
    """Get all users."""
    users = await users_service.get_users(db)
    return users


async def get_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Get user by id."""
    user = await users_service.get_user(db, user_id)
    if not user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)
    return user


async def refresh_token(user_agent: str, token: str, redis: AsyncRedis) -> str:
    """Refresh jwt token."""
    user_id = users_utils.decode_token(token=token)
    user_id_str = str(user_id)

    if not await redis.exists(user_id_str):
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    tokens = await redis.hgetall(user_id_str)

    if user_agent not in tokens or tokens[user_agent] != token:
        await redis.delete(user_id_str)
        raise Logger.create_response_error(error_key='access_not_denied', is_cookie_remove=True)

    new_token = users_utils.get_token(user_id=user_id)

    await redis.hset(user_id_str, user_agent, new_token)

    return new_token


async def get_current_user(token: str, db: AsyncSession, redis: AsyncRedis, user_agent: str) -> UserSchema:
    """Get and validate user token."""
    if not token:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_id = users_utils.decode_token(token=token)
    user_id_str = str(user_id)

    tokens = await redis.hgetall(user_id_str)

    if not await redis.exists(user_id_str):
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    if user_agent not in tokens or tokens[user_agent] != token:
        await redis.delete(user_id_str)
        raise Logger.create_response_error(error_key='access_not_denied', is_cookie_remove=True)

    user = await users_service.get_user(db=db, user_id=user_id)

    if not user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    return user


async def create_user(
    db: AsyncSession,
    redis: AsyncRedis,
    user_agent: str,
    user_create_data: user_create_model,
) -> create_user_result:
    """Create user."""
    user = await users_service.get_user_by_username(db=db, username=user_create_data.username)

    if user is not None:
        raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

    new_user = await users_service.create_user(db=db, user=user_create_data)

    token = users_utils.get_token(user_id=new_user.id)

    await redis.hset(str(new_user.id), user_agent, token)

    return create_user_result(token=token, user=new_user)


async def logout_user(token: str, user_agent: str, redis: AsyncRedis) -> str:
    """Logout user."""
    if not token:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_id = users_utils.decode_token(token=token)
    user_id_str = str(user_id)

    if not await redis.exists(user_id_str):
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    tokens = await redis.hgetall(user_id_str)

    if user_agent not in tokens or tokens[user_agent] != token:
        redis.delete(user_id_str)
        raise Logger.create_response_error(error_key='access_not_denied', is_cookie_remove=True)

    await redis.hdel(user_id_str, user_agent)

    return 'Successfully logged out'


async def login_user(
    db: AsyncSession,
    redis: AsyncRedis,
    user_agent: str,
    login_data: user_login_model,
) -> str:
    """Login user."""
    user = await users_service.get_user_by_username(db, login_data.username)

    if user is None:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)

    password_correct = users_utils.verify_password(login_data.password, user.password)

    if not password_correct:
        raise Logger.create_response_error(error_key='password_not_correct', is_cookie_remove=False)

    user_id_str = str(user.id)

    token = users_utils.get_token(user_id=user.id)

    await redis.hset(user_id_str, user_agent, token)

    return token
