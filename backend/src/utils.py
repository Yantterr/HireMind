from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.service as users_service
import src.users.utils as users_utils
from src.database import AsyncRedis
from src.logger import Logger
from src.users.models import UserModel


async def authorize_user(token: str, user_agent: str, db: AsyncSession, redis: AsyncRedis) -> UserModel:
    """Authorize user."""
    if not token:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_id = users_utils.decode_token(token=token)
    user_id_str = str(user_id)

    composite_key = f'{user_id_str}/agent:{user_agent}'

    allowed_composite_keys = await redis.keys(pattern=f'{user_id_str}/agent:*')

    redis_token = await redis.get(value=f'{user_id_str}/agent:{user_agent}')

    if composite_key not in allowed_composite_keys:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    if redis_token != token:
        await redis.delete(*allowed_composite_keys)

        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=True)

    user = await users_service.get_user(db=db, user_id=user_id)

    if user is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=True)

    return UserModel(username=user.username, id=user.id)


async def validate_login_data(request: Request) -> tuple[str, str]:
    """Validate login data."""
    token = request.cookies.get('token')

    if not token:
        raise Logger.create_response_error(error_key='user_not_authenticated')

    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error')

    return token, user_agent
