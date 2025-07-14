from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.logger import Logger
from src.models.generally_models import SystemRoleEnum
from src.schemas import UserSchema


async def get_users(db: AsyncSession) -> list[UserSchema]:
    """Service for get all users."""
    request = select(UserSchema)
    result = await db.execute(request)
    users = result.scalars().all()

    return list(users)


async def get_user(db: AsyncSession, user_id: int) -> UserSchema | None:
    """Service for get user by id."""
    request = select(UserSchema).where(UserSchema.id == user_id)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def get_user_by_email(db: AsyncSession, email: str) -> UserSchema | None:
    """Service for get user by username."""
    request = select(UserSchema).where(UserSchema.email == email)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def create_user(
    db: AsyncSession, role: SystemRoleEnum, password: Optional[str], username: Optional[str], email: Optional[str]
) -> UserSchema:
    """Service for create user."""
    new_user = UserSchema(
        username=username,
        password=password,
        email=email,
        role=role,
        is_activated=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


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
        user.role = role

    await db.commit()
    await db.refresh(user)

    return user
