from fastapi import APIRouter, Request, Response

import src.users.dependencies as users_dep
import src.utils as generally_utils
from src.config import settings
from src.database import RedisDep, SessionDep
from src.logger import Logger
from src.models import MessageModel
from src.schemas import UserSchema
from src.users.models import UserCreateModel, UserLoginModel, UserModel

users_router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@users_router.get('/', response_model=list[UserModel])
async def get_users(db: SessionDep) -> list[UserSchema]:
    """Get all users."""
    users = await users_dep.get_users(db=db)
    return users


@users_router.get('/me', response_model=UserModel)
async def get_current_user(
    request: Request,
    response: Response,
    db: SessionDep,
    redis: RedisDep,
) -> UserSchema:
    """Get current user by token from cookie."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)

    result = await users_dep.get_current_user(token=token, hash=hash, db=db, redis=redis, user_agent=user_agent)

    response.set_cookie(
        key='token',
        value=result.token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return result.user


@users_router.post('/login', response_model=MessageModel)
async def login_user(
    request: Request, response: Response, db: SessionDep, redis: RedisDep, login_data: UserLoginModel
) -> MessageModel:
    """Authenticate user and set token cookie."""
    user_agent = request.headers.get('user-agent')
    if not user_agent:
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

    return MessageModel(message='Login successful.')


@users_router.post('/logout', response_model=MessageModel)
async def logout_user(request: Request, response: Response, redis: RedisDep) -> MessageModel:
    """Logout user by deleting token cookie and invalidating token."""
    token = request.cookies.get('token')
    user_agent = request.headers.get('user-agent')

    if not token or not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    message = await users_dep.logout_user(token=token, user_agent=user_agent, redis=redis)
    response.delete_cookie(key='token')

    return MessageModel(message=message)


@users_router.post('/refresh', response_model=MessageModel)
async def refresh_token(request: Request, response: Response, db: SessionDep, redis: RedisDep) -> MessageModel:
    """Refresh JWT token and update cookie."""
    token = request.cookies.get('token')
    user_agent = request.headers.get('user-agent')

    if not token or not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    new_token = await users_dep.refresh_token(user_agent=user_agent, db=db, redis=redis, token=token)

    response.set_cookie(
        key='token',
        value=new_token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return MessageModel(message='Token was refreshed successfully.')


@users_router.post('/', response_model=UserModel)
async def create_user(
    request: Request, response: Response, db: SessionDep, redis: RedisDep, user_create_data: UserCreateModel
) -> UserSchema:
    """Create a new user and set token cookie."""
    _, hash, user_agent = await generally_utils.get_authorization_data(request=request)

    result = await users_dep.create_user(
        db=db, user_agent=user_agent, hash=hash, redis=redis, user_create_data=user_create_data
    )

    response.set_cookie(
        key='token',
        value=result.token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        secure=False,
        samesite='lax',
    )

    return result.user


@users_router.get('/{user_id}', response_model=UserModel)
async def get_user(db: SessionDep, user_id: int) -> UserSchema:
    """Get user by ID."""
    user = await users_dep.get_user(db=db, user_id=user_id)
    return user
