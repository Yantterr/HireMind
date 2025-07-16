from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

import src.utils.auth_utils as auth_utils
from src.config import settings
from src.database import session_factory
from src.dataclasses.auth_dataclasses import UserDataclass
from src.models.generally_models import SystemRoleEnum
from src.redis import get_redis
from src.schemas import UserSchema


class AnonymousUserTokenMiddleware(BaseHTTPMiddleware):
    """Middleware for check token in cookie."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        """Check token in cookie."""
        if (
            (request.url.path == '/auth/' and request.method == 'POST')
            or request.url.path == '/auth/login/'
            or request.cookies.get('token')
        ):
            return await call_next(request)

        user = UserSchema(role=SystemRoleEnum.ANONYM)

        async with session_factory() as session:
            async with session.begin():
                session.add(user)
                await session.flush()
                await session.refresh(user)

        token = auth_utils.get_token(UserDataclass.from_orm(user))

        redis = get_redis()
        user_agent = request.headers.get('user-agent')
        await redis.set(name=f'{user.id}/agent:{user_agent}', value=token, expire=2_592_000)

        request.state.token = token
        response = await call_next(request)

        response.set_cookie(value=token, **settings.auth_token_config)

        return response
