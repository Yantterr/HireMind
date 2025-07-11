from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi_mail import MessageType

import src.controllers.auth as auth_controllers
import src.dependencies.auth as auth_dependencies
import src.utils.generally as generally_utils
from src.config import settings
from src.database import SessionDep
from src.dataclasses.auth import AuthDataclass, UserDataclass
from src.logger import Logger
from src.models.generally import MessageModel
from src.models.user import UserConfirmEmailModel, UserCreateModel, UserLoginModel, UserModel
from src.redis import RedisDep
from src.schemas import UserSchema

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@auth_router.post('/', response_model=UserModel)
async def create_user(
    request: Request,
    response: Response,
    db: SessionDep,
    redis: RedisDep,
    background_tasks: BackgroundTasks,
    user_create_data: UserCreateModel,
) -> UserDataclass:
    """Create a new user."""
    token = request.cookies.get('token')
    user_agent = request.headers.get('user-agent')

    if not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    result = await auth_controllers.create_user(
        user_create_data=user_create_data, token=token, user_agent=user_agent, db=db, redis=redis
    )

    background_tasks.add_task(
        generally_utils.send_email_message, user_create_data.email, str(result.key), MessageType.plain
    )

    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@auth_router.post('/login', response_model=UserModel)
async def login_user(
    request: Request, response: Response, redis: RedisDep, db: SessionDep, login_data: UserLoginModel
) -> UserDataclass:
    """Login user."""
    user_agent = request.headers.get('user-agent')
    if not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    result = await auth_controllers.login_user(redis=redis, user_agent=user_agent, login_data=login_data, db=db)
    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@auth_router.post('/logout', response_model=MessageModel)
async def logout_user(
    response: Response,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> MessageModel:
    """Logout user."""
    message = await auth_controllers.logout_user(
        user_id=auth_data.user.id, user_agent=auth_data.user_agent, redis=redis
    )

    response.delete_cookie(key='token')

    return MessageModel(message=message)


@auth_router.get('/me', response_model=UserModel)
async def get_current_user(
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> UserDataclass:
    """Get current user by token from cookie."""
    return auth_data.user


@auth_router.post('/refresh', response_model=UserModel)
async def refresh_token(
    response: Response,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> UserDataclass:
    """Refresh JWT token and update cookie."""
    user = auth_data.user

    new_token = await auth_controllers.refresh_token(user=user, user_agent=auth_data.user_agent, redis=redis)
    response.set_cookie(value=new_token, **settings.auth_token_config)

    return user


@auth_router.patch('/confirm_email', response_model=UserModel)
async def confirm_email(
    response: Response,
    confirm_email_data: UserConfirmEmailModel,
    db: SessionDep,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> UserDataclass:
    """Confirm email."""
    result = await auth_controllers.confirm_email(
        user_id=auth_data.user.id, user_agent=auth_data.user_agent, key=confirm_email_data.key, db=db, redis=redis
    )

    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user
