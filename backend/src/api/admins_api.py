from typing import Annotated

from fastapi import APIRouter, Depends, Request

import src.controllers.chats_controllers as chats_controllers
import src.controllers.users_controllers as users_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.dependencies.generally_dependencies as generally_dependencies
import src.services.admins_services as admins_services
import src.services.users_services as users_services
from src.dto.chats_dto import ChatsAdminPaginatedDataclass, EventsPaginatedDataclass
from src.dto.users_dto import UserDataclass
from src.engines.database_engine import SessionDep
from src.models.chats_models import ChatsAdminModel, EventCreateModel, EventModel, EventPaginatedModel
from src.models.generally_models import PaginatedResponseModel, PaginationParamsModel, SystemRoleEnum
from src.models.users_models import UserModel
from src.schemas import EventSchema, UserSchema

admins_router = APIRouter(
    prefix='/admins',
    tags=['admins'],
)


@admins_router.get('/chats', response_model=ChatsAdminModel)
async def chats_get_all(
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('admin'))],
    db: SessionDep,
) -> ChatsAdminPaginatedDataclass:
    """Get all GPT chats."""
    page, per_page = pagination_params.page, pagination_params.per_page
    chats = await chats_controllers.chats_admin_get_all(
        db=db, user_id=user.id, role=user.role, page=page, per_page=per_page
    )

    return chats


@admins_router.get('/events', response_model=EventPaginatedModel)
async def event_get_all(
    request: Request,
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    db: SessionDep,
) -> EventsPaginatedDataclass:
    """Get all GPT events."""
    await auth_dependencies.require_permission('admin')(request=request)
    page, per_page = pagination_params.page, pagination_params.per_page
    events = await chats_controllers.event_get_all(db=db, page=page, per_page=per_page)

    return events


@admins_router.post('/events', response_model=EventModel)
async def event_create(
    request: Request,
    event_create_data: EventCreateModel,
    db: SessionDep,
) -> EventSchema:
    """Create a new GPT event."""
    await auth_dependencies.require_permission('admin')(request=request)
    event = await chats_controllers.event_create(db=db, event_create_data=event_create_data)

    return event


@admins_router.get('/users', response_model=PaginatedResponseModel[UserModel])
async def get_all_users(
    request: Request,
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    db: SessionDep,
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


@admins_router.get('/', response_model=PaginatedResponseModel[UserModel])
async def get_all_admins(
    request: Request,
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    db: SessionDep,
) -> PaginatedResponseModel[UserModel]:
    """Get list of admins."""
    await auth_dependencies.require_permission('admin')(request=request)
    admins, page, per_page, total_items, total_pages = await admins_services.get_all_admins(
        db=db, page=pagination_params.page, per_page=pagination_params.per_page
    )

    return PaginatedResponseModel(
        items=[UserModel.model_validate(admin) for admin in admins],
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )


@admins_router.get('/users/{user_id}', response_model=UserModel)
async def get_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Get user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.get_user(db=db, user_id=user_id)

    return user


@admins_router.delete('/users/{user_id}', response_model=UserModel)
async def delete_user(user_id: int, db: SessionDep, request: Request) -> UserSchema:
    """Delete user by id."""
    await auth_dependencies.require_permission('admin')(request=request)
    user = await users_controllers.delete_user(db=db, user_id=user_id)

    return user


@admins_router.delete('/{admin_id}', response_model=UserModel)
async def delete_admin(request: Request, admin_id: int, db: SessionDep) -> UserSchema:
    """Changes the role from admin to user."""
    await auth_dependencies.require_permission('admin')(request=request)
    admin = await users_services.edit_user(db=db, user_id=admin_id, role=SystemRoleEnum.USER)

    return admin


@admins_router.post('/{user_id}', response_model=UserModel)
async def create_admin(request: Request, user_id: int, db: SessionDep) -> UserSchema:
    """Changes the user role from user to admin."""
    await auth_dependencies.require_permission('admin')(request=request)
    admin = await users_services.edit_user(db=db, user_id=user_id, role=SystemRoleEnum.ADMIN)

    return admin
