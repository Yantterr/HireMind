from fastapi import APIRouter, Request, Response

import src.users.dependencies as users_dep
from src.config import settings
from src.database import RedisDep, SessionDep
from src.logger import Logger
from src.models import message_model
from src.users.models import user_create_model, user_login_model, user_model, users_model
from src.users.schemas import UserSchema

users_router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@users_router.get('/', response_model=users_model)
async def get_users(
    db: SessionDep,
) -> list[UserSchema]:
    """Endpoint for get all users."""
    users: list[UserSchema] = await users_dep.get_users(db=db)
    return users


@users_router.get('/me', response_model=user_model)
async def get_current_user(
    request: Request,
    db: SessionDep,
    redis: RedisDep,
) -> UserSchema:
    """Get user by cookie token."""
    token = request.cookies.get('token')
    if token is None:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    user: UserSchema = await users_dep.get_current_user(db=db, user_agent=user_agent, token=token, redis=redis)
    return user


@users_router.post('/login', response_model=message_model)
async def login_user(
    request: Request, response: Response, db: SessionDep, redis: RedisDep, login_data: user_login_model
) -> str:
    """Login user."""
    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    token = await users_dep.login_user(db=db, redis=redis, user_agent=user_agent, login_data=login_data)

    response.set_cookie(
        key='token',
        value=token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return 'Login successful.'


@users_router.post('/logout', response_model=message_model)
async def logout_user(request: Request, response: Response, redis: RedisDep) -> str:
    """Logout user."""
    token = request.cookies.get('token')
    if token is None:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    message = await users_dep.logout_user(token=token, user_agent=user_agent, redis=redis)
    response.delete_cookie(key='token')

    return message


@users_router.post('/refresh', response_model=message_model)
async def refresh_token(request: Request, response: Response, redis: RedisDep) -> message_model:
    """Refresh jwt token."""
    token = request.cookies.get('token')
    if token is None:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    new_token = await users_dep.refresh_token(user_agent=user_agent, redis=redis, token=token)

    response.set_cookie(
        key='token',
        value=new_token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return message_model(message='Token was refreshed successful.')


@users_router.post('/', response_model=user_model)
async def create_user(
    request: Request, response: Response, db: SessionDep, redis: RedisDep, user_create_data: user_create_model
) -> UserSchema:
    """Create user."""
    user_agent = request.headers.get('user-agent')

    if user_agent is None:
        raise Logger.create_response_error(error_key='undefined_error', is_cookie_remove=False)

    result = await users_dep.create_user(db=db, user_agent=user_agent, redis=redis, user_create_data=user_create_data)

    response.set_cookie(
        key='token',
        value=result.token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return result.user


@users_router.get('/{user_id}', response_model=user_model)
async def get_user(db: SessionDep, user_id: int) -> UserSchema:
    """Get user by id."""
    user = await users_dep.get_user(db=db, user_id=user_id)
    return user
