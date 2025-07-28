from sqlalchemy.ext.asyncio import AsyncSession

import src.services.users_services as users_service
from src.logger import Logger
from src.schemas import UserSchema


async def get_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Controller for get user by id."""
    user = await users_service.get_user(db=db, user_id=user_id)

    if not user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)

    return user


async def delete_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Controller for delete user by id."""
    removed_user = await users_service.delete_user(db=db, user_id=user_id)

    if not removed_user:
        raise Logger.create_response_error(error_key='user_not_found', is_cookie_remove=False)

    return removed_user
