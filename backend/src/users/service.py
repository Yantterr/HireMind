from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import src.users.utils as users_utils
from src.schemas import UserSchema
from src.users.models import UserCreateModel


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


async def create_user(db: AsyncSession, user: UserCreateModel) -> UserSchema:
    """Service for create user."""
    new_user = UserSchema(username=user.username, password=users_utils.get_password_hash(user.password))

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
