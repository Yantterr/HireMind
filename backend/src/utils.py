from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

import src.anonymous.service as anonymous_service
import src.users.service as users_service
import src.users.utils as users_utils
from src.database import AsyncRedis
from src.logger import Logger
from src.models import SystemRoleEnum
from src.schemas import UserSchema


async def get_user_id_by_token(token: str, user_agent: str, redis: AsyncRedis) -> int:
    """Authorize user by token."""
    user_id = users_utils.decode_token(token=token)
    user_id_str = str(user_id)

    composite_key = f'{user_id_str}/agent:{user_agent}'

    allowed_composite_keys = await redis.keys(pattern=f'{user_id_str}/agent:*')

    if composite_key not in allowed_composite_keys:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    redis_token = await redis.get(value=f'{user_id_str}/agent:{user_agent}')

    if redis_token != token:
        await redis.delete(*allowed_composite_keys)

        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=True)

    return user_id


async def get_user_by_hash(
    hash: str,
    db: AsyncSession,
) -> UserSchema:
    """Get user by hash."""
    user_id = await anonymous_service.get_user_id(db=db, hash=hash)

    if user_id:
        user = UserSchema(username=None, role=SystemRoleEnum.ANONYM, id=user_id, password=None)

        return user

    new_user = await users_service.create_user(db=db, password=None, username=None, role=SystemRoleEnum.ANONYM)

    if not await anonymous_service.save_user_id(db=db, user_id=new_user.id, hash=hash):
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    return new_user


async def save_token(user_id: int, user_agent: str, redis: AsyncRedis) -> str:
    """Save token to redis."""
    token = users_utils.get_token(user_id=user_id)

    user_id_str = str(user_id)

    await redis.set(name=f'{user_id_str}/agent:{user_agent}', value=token, expire=2_592_000)

    return token


# async def authorize_user(token: str, user_agent: str, db: AsyncSession, redis: AsyncRedis) -> UserModel:
#     """Authorize user."""
#     if not token:
#         raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

#     user_id = users_utils.decode_token(token=token)
#     user_id_str = str(user_id)

#     composite_key = f'{user_id_str}/agent:{user_agent}'

#     allowed_composite_keys = await redis.keys(pattern=f'{user_id_str}/agent:*')

#     redis_token = await redis.get(value=f'{user_id_str}/agent:{user_agent}')

#     if composite_key not in allowed_composite_keys:
#         raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

#     if redis_token != token:
#         await redis.delete(*allowed_composite_keys)

#         raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=True)

#     user = await users_service.get_user(db=db, user_id=user_id)

#     if user is None:
#         raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=True)

#     return UserModel(username=user.username, role=SystemRoleEnum(user.role), id=user.id)


# async def validate_login_data(request: Request, redis: AsyncRedis, db: AsyncSession) -> tuple[str, str]:
#     """Validate login data."""
#     token = request.cookies.get('token')
#     hash = request.query_params.get('hash')

#     if not token and not hash:
#         raise Logger.create_response_error(error_key='user_not_authenticated')

#     user_agent = request.headers.get('user-agent')

#     if user_agent is None:
#         raise Logger.create_response_error(error_key='undefined_error')

#     if not token and hash:
#         user_id = await users_service.get_user_id(db=db, hash=hash)
#         if user_id:
#             return await authorize_user(
#                 token=users_utils.get_token(user_id=user_id), user_agent=user_agent, db=db, redis=redis
#             )

#         # token = users_utils.get_token(user_id=hash)

#     return token, user_agent
