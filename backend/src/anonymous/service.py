from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.schemas import AnonymousUserSchema


async def get_user_id(db: AsyncSession, hash: str) -> int | None:
    """Service for get user id by hash."""
    request = select(AnonymousUserSchema.user_id).where(AnonymousUserSchema.hash == hash)
    result = await db.execute(request)
    user_id = result.scalars().first()

    return user_id


async def save_user_id(db: AsyncSession, user_id: int, hash: str) -> bool:
    """Service for save user id by hash."""
    try:
        new_user = AnonymousUserSchema(user_id=user_id, hash=hash)

        db.add(new_user)
        await db.commit()

        return True
    except Exception:
        print('Error save user id by hash')
        return False


async def delete_user_id(db: AsyncSession, user_id: int) -> bool:
    """Service for delete user id by hash."""
    await db.execute(delete(AnonymousUserSchema).where(AnonymousUserSchema.user_id == user_id))
    await db.commit()

    return True
