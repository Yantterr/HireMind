from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.generally_models import SystemRoleEnum
from src.schemas import UserSchema


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


async def delete_user(db: AsyncSession, user_id: int) -> UserSchema | None:
    """Service for delete user by id."""
    request = select(UserSchema).where(UserSchema.id == user_id)
    result = await db.execute(request)
    user = result.scalars().first()

    return user
