from typing import Annotated

from fastapi import Depends, Request

import src.utils.auth_utils as auth_utils
from src.dataclasses.auth_dataclasses import AuthDataclass
from src.logger import Logger
from src.redis import RedisDep


def get_validated_auth_info(request: Request) -> dict[str, str]:
    """Get token and user agent from request and validate them."""
    cookie_token = request.cookies.get('token')
    user_agent = request.headers.get('User-Agent')

    if hasattr(request.state, 'token'):
        state_token = request.state.token
        if not isinstance(state_token, str):
            raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    if not user_agent or (not cookie_token and not state_token):
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    token = cookie_token or state_token

    return {'token': token, 'user_agent': user_agent}


async def get_current_user(
    redis: RedisDep, auth_info: Annotated[dict[str, str], Depends(get_validated_auth_info)]
) -> AuthDataclass:
    """Get current user by token from cookie."""
    token, user_agent = auth_info['token'], auth_info['user_agent']

    user = auth_utils.decode_token(token=token)

    user_id_str = str(user.id)
    composite_key = f'{user_id_str}/agent:{user_agent}'

    allowed_composite_keys = await redis.keys(pattern=f'{user_id_str}/agent:*')

    if composite_key not in allowed_composite_keys:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=True)

    redis_token = await redis.get(value=f'{user_id_str}/agent:{user_agent}')

    if redis_token != token:
        await redis.delete(*allowed_composite_keys)
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=True)

    return AuthDataclass(user=user, user_agent=user_agent, token=token)
