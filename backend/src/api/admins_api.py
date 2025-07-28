from fastapi import APIRouter

import src.services.admins_services as admins_services
import src.services.users_services as users_services
from src.engines.database_engine import SessionDep
from src.models.auth_models import UserModel
from src.models.generally_models import SystemRoleEnum
from src.schemas import UserSchema

admins_router = APIRouter(
    prefix='/admins',
    tags=['admins'],
)


@admins_router.get('/', response_model=list[UserModel])
async def get_all_admins(db: SessionDep) -> list[UserSchema]:
    """Get all admins."""
    admins = await admins_services.get_all_admins(db=db)

    return admins


@admins_router.delete('/{admin_id}', response_model=UserModel)
async def delete_admin(admin_id: int, db: SessionDep) -> UserSchema:
    """Delete admin by id."""
    admin = await users_services.edit_user(db=db, user_id=admin_id, role=SystemRoleEnum.USER)

    return admin


@admins_router.post('/{admin_id}', response_model=UserModel)
async def create_admin(admin_id: int, db: SessionDep) -> UserSchema:
    """Create admin by id."""
    admin = await users_services.edit_user(db=db, user_id=admin_id, role=SystemRoleEnum.ADMIN)

    return admin
