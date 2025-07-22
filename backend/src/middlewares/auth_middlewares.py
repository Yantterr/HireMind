from fastapi import Request, status
from fastapi.responses import JSONResponse
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
            or request.url.path == '/auth/login'
            or request.cookies.get('token')
        ):
            return await call_next(request)

        user = UserSchema(role=SystemRoleEnum.ANONYM)

        async with session_factory() as session:
            async with session.begin():
                session.add(user)
                await session.flush()
                await session.refresh(user)

        token = auth_utils.token_generate(UserDataclass.from_orm(user))

        redis = get_redis()
        user_agent = request.headers.get('user-agent')
        await redis.set(name=f'{user.id}/agent:{user_agent}', value=token, expire=2_592_000)

        request.state.token = token
        request.state.user = user
        response = await call_next(request)

        response.set_cookie(value=token, **settings.auth_token_config)

        return response


class ValidateTokenAndAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for validate token."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        """Validate token."""
        if (
            (request.url.path == '/auth/' and request.method == 'POST')
            or request.url.path == '/auth/login'
            or request.url.path == '/auth/login/'
        ):
            return await call_next(request)

        auth_info = auth_utils.get_validated_auth_info(request)

        if auth_info.error == 'user_not_authenticated':
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content={'detail': 'User not authenticated.'}
            )
        elif auth_info.error == 'undefined_error':
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={'detail': 'Undefined error.'}
            )

        token, user_agent = auth_info.token, auth_info.user_agent
        user, is_expired = auth_utils.token_expire_verify(token=token)
        request.state.user = user

        if not is_expired:
            return await call_next(request)

        new_token = auth_utils.token_generate(user=user)
        redis = get_redis()
        token, error = await auth_utils.token_save(
            old_token=token, new_token=new_token, user_agent=user_agent, user_id=user.id, redis=redis
        )

        if error == 'access_denied':
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={'detail': 'Access denied.'},
                headers={'set-cookie': 'token=; Max-Age=0; Path=/; secure=true; SameSite=none'},
            )

        response = await call_next(request)
        response.set_cookie(value=new_token, **settings.auth_token_config)

        return response
