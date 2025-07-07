from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import src.users.utils as users_utils
from src.models import SystemRoleEnum
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


async def get_user_by_username(db: AsyncSession, username: str) -> UserSchema | None:
    """Service for get user by username."""
    request = select(UserSchema).where(UserSchema.username == username)
    result = await db.execute(request)
    user = result.scalars().first()

    return user


async def create_user(
    db: AsyncSession, password: Optional[str], username: Optional[str], role: SystemRoleEnum
) -> UserSchema:
    """Service for create user."""
    new_user = UserSchema(
        username=username,
        password=users_utils.get_password_hash(password) if password is not None else None,
        role=role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
