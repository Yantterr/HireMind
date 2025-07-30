from typing import Annotated

from fastapi import APIRouter, Depends, Request

import src.dependencies.auth_dependencies as auth_dependencies
import src.dependencies.generally_dependencies as generally_dependencies
import src.services.admins_services as admins_services
import src.services.users_services as users_services
from src.engines.database_engine import SessionDep
from src.models.auth_models import UserModel
from src.models.generally_models import PaginatedResponseModel, PaginationParamsModel, SystemRoleEnum
from src.schemas import UserSchema

admins_router = APIRouter(
    prefix='/admins',
    tags=['admins'],
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
