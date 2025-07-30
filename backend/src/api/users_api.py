from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi_mail import MessageType

import src.controllers.users_controllers as users_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.dependencies.generally_dependencies as generally_dependencies
import src.services.users_services as users_services
import src.utils.auth_utils as auth_utils
import src.utils.generally_utils as generally_utils
from src.config import settings
from src.dataclasses.users_dataclasses import UserDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger
from src.models.auth_models import UserKeyModel
from src.models.generally_models import PaginatedResponseModel, PaginationParamsModel, ResponseModel
from src.models.users_models import UserEditEmailModel, UserEditNameModel, UserModel, UserResetPasswordModel
from src.schemas import UserSchema

users_router = APIRouter(prefix='/users', tags=['users'])


@users_router.get('/me', response_model=UserModel)
async def get_current_user(
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('anonym'))],
) -> UserDataclass:
    """Get current user by token from cookie."""
    return user


@users_router.get('/email-key', response_model=ResponseModel)
async def get_new_key(
    request: Request,
    redis: RedisDep,
    db: SessionDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
    background_tasks: BackgroundTasks,
) -> ResponseModel:
    """Get new key for email confirmation."""
    auth_info = auth_utils.get_validated_auth_info(request)

    new_key = await users_controllers.email_new_key(user_agent=auth_info.user_agent, user_id=user.id, redis=redis)
    user_orm = await users_services.get_user_by_id(db=db, user_id=user.id)

    if not user_orm or not user_orm.email:
        raise Logger.create_response_error(error_key='user_not_authenticated', is_cookie_remove=False)

    background_tasks.add_task(generally_utils.send_email_message, user_orm.email, str(new_key), MessageType.plain)

    return ResponseModel(message='New key was generated successfully.')


@users_router.patch('/confirm-email', response_model=UserModel)
async def confirm_email(
    request: Request,
    response: Response,
    confirm_email_data: UserKeyModel,
    db: SessionDep,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> UserDataclass:
    """Confirm email by access key."""
    auth_info = auth_utils.get_validated_auth_info(request)
    if auth_info.error:
        raise Logger.create_response_error(error_key=auth_info.error, is_cookie_remove=False)

    result = await users_controllers.confirm_email(
        user_id=user.id, user_agent=auth_info.user_agent, key=confirm_email_data.key, db=db, redis=redis
    )

    response.set_cookie(value=result.token, **settings.auth_token_config)
    return result.user


@users_router.patch('/change-email', response_model=UserModel)
async def edit_email(
    request: Request,
    response: Response,
    edit_email_data: UserEditEmailModel,
    db: SessionDep,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> UserDataclass:
    """Change email by access key."""
    user_agent = auth_utils.get_validated_auth_info(request).user_agent
    result = await users_controllers.edit_email(
        db=db,
        user_id=user.id,
        user_agent=user_agent,
        key=edit_email_data.key,
        redis=redis,
        new_email=edit_email_data.email,
    )

    response.delete_cookie('token')
    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@users_router.patch('/change-username', response_model=UserModel)
async def change_username(
    request: Request,
    response: Response,
    change_username_data: UserEditNameModel,
    db: SessionDep,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
):
    """Change username by access key."""
    user_agent = auth_utils.get_validated_auth_info(request).user_agent
    result = await users_controllers.edit_username(
        user_id=user.id,
        user_agent=user_agent,
        db=db,
        redis=redis,
        username=change_username_data.username,
    )

    response.delete_cookie('token')
    response.set_cookie(value=result.token, **settings.auth_token_config)

    return result.user


@users_router.post('/forgot-password', response_model=ResponseModel)
async def forgot_password(
    request: Request,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
    redis: RedisDep,
    background_tasks: BackgroundTasks,
) -> ResponseModel:
    """Send a confirmation code to the email address of the user."""
    user_agent = auth_utils.get_validated_auth_info(request).user_agent
    key = users_controllers.forgot_password(user=user, user_agent=user_agent, redis=redis)

    background_tasks.add_task(generally_utils.send_email_message, user.email, str(key), MessageType.plain)
    return ResponseModel(message='Message was sent successfully to your email.')


@users_router.patch('/reset-password', response_model=ResponseModel)
async def reset_password(
    request: Request,
    reset_password_data: UserResetPasswordModel,
    db: SessionDep,
    redis: RedisDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> ResponseModel:
    """Reset password by access key."""
    auth_info = auth_utils.get_validated_auth_info(request)

    result = await users_controllers.reset_password(
        user_agent=auth_info.user_agent,
        user=user,
        key=reset_password_data.key,
        db=db,
        new_password=reset_password_data.password,
        redis=redis,
    )

    return ResponseModel(message=result)


@users_router.patch('/change-password', response_model=ResponseModel)
async def edit_password(
    edit_password_data: UserResetPasswordModel,
    db: SessionDep,
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('user'))],
) -> ResponseModel:
    """Change password."""
    result = await users_controllers.edit_password(db=db, user_id=user.id, new_password=edit_password_data.password)

    return ResponseModel(message=result)


@users_router.get('/', response_model=PaginatedResponseModel[UserModel])
async def get_all_users(
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    db: SessionDep,
    request: Request,
) -> PaginatedResponseModel[UserModel]:
    """Get list of users."""
    await auth_dependencies.require_permission('admin')(request=request)
    users, page, per_page, total_items, total_pages = await users_services.get_users(
        db=db, page=pagination_params.page, per_page=pagination_params.per_page
    )

    return PaginatedResponseModel(
        items=[UserModel.model_validate(user) for user in users],
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )


@users_router.get('/{user_id}', response_model=UserModel)
async def get_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Get user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.get_user(db=db, user_id=user_id)

    return user


@users_router.delete('/{user_id}', response_model=UserModel)
async def delete_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Delete user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.delete_user(db=db, user_id=user_id)

    return user
