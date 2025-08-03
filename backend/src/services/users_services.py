from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from src.logger import Logger
from src.models.generally_models import SystemRoleEnum
from src.schemas import UserSchema


async def get_users(db: AsyncSession, page: int, per_page: int) -> tuple[list[UserSchema], int, int, int, int]:
    """Service for get all users."""
    base_query = select(UserSchema)

    count_query = base_query.with_only_columns(func.count())
    total_result = await db.execute(count_query)
    total_items = total_result.scalar_one()

    total_pages = (total_items + per_page - 1) // per_page
    offset = (page - 1) * per_page

    data_query = (
        base_query.offset(offset)
        .limit(per_page)
        .options(
            load_only(UserSchema.id, UserSchema.role, UserSchema.username, UserSchema.email, UserSchema.is_activated)
        )
        .order_by(UserSchema.updated_at.desc())
    )

    result = await db.execute(data_query)
    users = result.scalars().all()

    return list(users), page, per_page, total_items, total_pages


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserSchema | None:
    """Service for get user by id."""
    request = select(UserSchema).where(UserSchema.id == user_id)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> UserSchema | None:
    """Service for get user by email."""
    request = select(UserSchema).where(UserSchema.email == email)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def get_user_by_username(db: AsyncSession, username: str) -> UserSchema | None:
    """Service for get user by username."""
    request = select(UserSchema).where(UserSchema.username == username)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def get_user_password(db: AsyncSession, user_id: int) -> UserSchema | None:
    """Service for get user by id."""
    request = select(UserSchema).where(UserSchema.id == user_id).options(load_only(UserSchema.password))
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def edit_user(
    db: AsyncSession,
    user_id: int,
    email: Optional[str] = None,
    is_activated: Optional[bool] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    role: Optional[SystemRoleEnum] = None,
) -> UserSchema:
    """Service for edit user."""
    request = select(UserSchema).where(UserSchema.id == user_id)
    result = await db.execute(request)
    user = result.scalars().first()

    if user is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    if username:
        user.username = username

    if password:
        user.password = password

    if is_activated is not None:
        user.is_activated = is_activated

    if email:
        user.email = email

    if role:
        user.role = SystemRoleEnum.ADMIN

    await db.commit()
    await db.refresh(user)

    return user
