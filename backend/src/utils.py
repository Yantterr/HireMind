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
    """Validate token and user agent in Redis and return user ID."""
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
    """Get or create anonymous user by hash."""
    user_id = await anonymous_service.get_user_id(db=db, hash=hash)

    if user_id:
        user = UserSchema(username=None, role=SystemRoleEnum.ANONYM, id=user_id, password=None)

        return user

    new_user = await users_service.create_user(db=db, password=None, username=None, role=SystemRoleEnum.ANONYM)

    if not await anonymous_service.save_user_id(db=db, user_id=new_user.id, hash=hash):
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    return new_user


async def save_token(user_id: int, user_agent: str, redis: AsyncRedis) -> str:
    """Generate and save JWT token in Redis."""
    token = users_utils.get_token(user_id=user_id)

    user_id_str = str(user_id)

    await redis.set(name=f'{user_id_str}/agent:{user_agent}', value=token, expire=2_592_000)

    return token


async def get_user_id(
    hash: Optional[str], token: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> int:
    """Get user ID by token or hash, raise if missing."""
    if token:
        return await get_user_id_by_token(token=token, user_agent=user_agent, redis=redis)
    elif hash:
        return (await get_user_by_hash(hash=hash, db=db)).id

    raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)


async def get_authorization_data(request: Request) -> tuple[Optional[str], Optional[str], str]:
    """Extract token, hash, and user-agent from request."""
    token = request.cookies.get('token')
    hash = request.query_params.get('hash')
    user_agent = request.headers.get('user-agent')

    if not user_agent or (not token and not hash):
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    return token, hash, user_agent
