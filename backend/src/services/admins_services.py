from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.generally_models import SystemRoleEnum
from src.schemas import UserSchema


async def get_all_admins(db: AsyncSession) -> list[UserSchema]:
    """Service for get all admins."""
    request = select(UserSchema).where(UserSchema.role == SystemRoleEnum.ADMIN)
    result = await db.execute(request)
    admins = result.scalars().all()

    return list(admins)
