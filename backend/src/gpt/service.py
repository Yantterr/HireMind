from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.database import AsyncSession
from src.schemas import ChatSchema


async def create_chat(db: AsyncSession, user_id: int, title: Optional[str]) -> ChatSchema:
    """Create a new GPT chat with optional title."""
    new_chat = ChatSchema(user_id=user_id, title=title)

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat, attribute_names=['messages'])

    return new_chat


async def get_all_chats(user_id: int, db: AsyncSession) -> list[ChatSchema]:
    """Retrieve all non-archived chats for a user."""
    request = select(ChatSchema).where(ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
    result = await db.execute(request)
    chats = result.scalars().all()

    return list(chats)


async def get_count_chats(db: AsyncSession, user_id: int, is_archived: bool) -> int:
    """Get the total number of non-archived or archived chats."""
    stmt = (
        select(func.count())
        .select_from(ChatSchema)
        .where(ChatSchema.is_archived == is_archived, ChatSchema.user_id == user_id)
    )
    result = await db.execute(stmt)
    count = result.scalar_one()
    return count


async def get_chat_by_id(chat_id: int, user_id: int, db: AsyncSession) -> Optional[ChatSchema]:
    """Get a non-archived chat by ID and user ID, including messages."""
    request = (
        select(ChatSchema)
        .options(selectinload(ChatSchema.messages))
        .where(ChatSchema.id == chat_id, ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    return chat


async def delete_chat(db: AsyncSession, user_id: int, chat_id: int) -> bool:
    """Soft-delete a chat by marking it as archived."""
    request = select(ChatSchema).where(
        ChatSchema.id == chat_id, ChatSchema.user_id == user_id, ~ChatSchema.is_archived
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    if chat is None:
        return False

    chat.is_archived = True
    await db.commit()

    return True
