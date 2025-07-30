from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from src.models.generally_models import SystemRoleEnum
from src.schemas import ChatSchema, UserSchema


async def get_all_admins(db: AsyncSession, page: int, per_page: int) -> tuple[list[UserSchema], int, int, int, int]:
    """Service for get all admins."""
    base_query = select(UserSchema).where(UserSchema.role == SystemRoleEnum.ADMIN)

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
    )

    result = await db.execute(data_query)
    admins = result.scalars().all()

    return list(admins), page, per_page, total_items, total_pages
