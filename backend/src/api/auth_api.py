from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi_mail import MessageType

import src.controllers.auth_controllers as auth_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.utils.auth_utils as auth_utils
import src.utils.generally_utils as generally_utils
from src.config import settings
from src.dto.auth_dto import UserDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger
from src.models.auth_models import AuthCreateModel, AuthLoginModel
from src.models.generally_models import ResponseModel
from src.models.users_models import UserModel

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@auth_router.post('/register', response_model=UserModel)
async def create_user(
    request: Request,
    response: Response,
    db: SessionDep,
    redis: RedisDep,
    background_tasks: BackgroundTasks,
    user_create_data: AuthCreateModel,
) -> UserDataclass:
    """Register a new user and send a confirmation code."""
    token = request.cookies.get('token')
    user_agent = request.headers.get('user-agent')

    if not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    result = await auth_controllers.create_user(
        user_create_data=user_create_data,
        token=token,
        user_agent=user_agent,
        db=db,
        redis=redis,
    )

    background_tasks.add_task(
        generally_utils.send_email_message, user_create_data.email, str(result.key), MessageType.plain
    )

    response.delete_cookie('token')
    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@auth_router.post('/login', response_model=UserModel)
async def login_user(
    request: Request, response: Response, redis: RedisDep, db: SessionDep, login_data: AuthLoginModel
) -> UserDataclass:
    """Login user."""
    user_agent = request.headers.get('user-agent')
    if not user_agent:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    result = await auth_controllers.login_user(redis=redis, user_agent=user_agent, login_data=login_data, db=db)
    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@auth_router.post('/logout', response_model=ResponseModel)
async def logout_user(
    response: Response,
    request: Request,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> ResponseModel:
    """Logout user and delete token from cookie."""
    auth_info = auth_utils.get_validated_auth_info(request)
    if auth_info.error:
        raise Logger.create_response_error(error_key=auth_info.error, is_cookie_remove=False)

    message = await auth_controllers.logout_user(user_id=user.id, user_agent=auth_info.user_agent, redis=redis)

    response.delete_cookie(key='token')

    return ResponseModel(message=message)
