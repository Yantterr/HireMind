from fastapi import APIRouter, BackgroundTasks, Request, Response
from fastapi_mail import MessageType

import src.controllers.auth_controllers as auth_controllers
import src.services.auth_services as auth_service
import src.utils.auth_utils as auth_utils
import src.utils.generally_utils as generally_utils
from src.config import settings
from src.database import SessionDep
from src.dataclasses.auth_dataclasses import UserDataclass
from src.logger import Logger
from src.models.auth_models import UserConfirmEmailModel, UserCreateModel, UserLoginModel, UserModel
from src.models.generally_models import ResponseModel, SystemRoleEnum
from src.redis import RedisDep

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
    request: Request, response: Response, redis: RedisDep, db: SessionDep, login_data: UserLoginModel
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
) -> ResponseModel:
    """Logout user."""
    auth_info = auth_utils.get_validated_auth_info(request)
    if auth_info.error:
        raise Logger.create_response_error(error_key=auth_info.error, is_cookie_remove=False)

    user = request.state.user
    message = await auth_controllers.logout_user(user_id=user.id, user_agent=auth_info.user_agent, redis=redis)

    response.delete_cookie(key='token')

    return ResponseModel(message=message)


@auth_router.get('/me', response_model=UserModel)
async def get_current_user(
    request: Request,
) -> UserDataclass:
    """Get current user by token from cookie."""
    user = request.state.user
    return user


@auth_router.get('/key', response_model=ResponseModel)
async def get_new_key(
    request: Request,
    redis: RedisDep,
    db: SessionDep,
    background_tasks: BackgroundTasks,
) -> ResponseModel:
    """Get new key for email confirmation."""
    auth_info = auth_utils.get_validated_auth_info(request)
    user_state = request.state.user

    new_key = await auth_controllers.email_new_key(user_agent=auth_info.user_agent, user_id=user_state.id, redis=redis)
    user_orm = await auth_service.get_user(db=db, user_id=user_state.id)

    if not user_orm or not user_orm.email:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    background_tasks.add_task(generally_utils.send_email_message, user_orm.email, str(new_key), MessageType.plain)

    return ResponseModel(message='New key was generated successfully.')


@auth_router.patch('/confirm_email', response_model=UserModel)
async def confirm_email(
    request: Request,
    response: Response,
    confirm_email_data: UserConfirmEmailModel,
    db: SessionDep,
    redis: RedisDep,
) -> UserDataclass:
    """Confirm email."""
    auth_info = auth_utils.get_validated_auth_info(request)
    if auth_info.error:
        raise Logger.create_response_error(error_key=auth_info.error, is_cookie_remove=False)

    user = request.state.user
    result = await auth_controllers.confirm_email(
        user_id=user.id, user_agent=auth_info.user_agent, key=confirm_email_data.key, db=db, redis=redis
    )

    response.set_cookie(value=result.token, **settings.auth_token_config)
    return result.user
