from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import AsyncSession
from src.schemas import ChatSchema


async def create_chat(db: AsyncSession, user_id: int, title: Optional[str]) -> ChatSchema:
    """Create gpt chat."""
    new_chat = ChatSchema(user_id=user_id, title=title)

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat, attribute_names=['messages'])

    return new_chat


async def get_all_chats(user_id: int, db: AsyncSession) -> list[ChatSchema]:
    """Get all chats by user id."""
    request = select(ChatSchema).where(ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
    result = await db.execute(request)
    chats = list(result.scalars().all())

    return chats


async def get_chat_by_id(chat_id: int, user_id: int, db: AsyncSession) -> ChatSchema | None:
    """Get chat by id."""
    request = (
        select(ChatSchema)
        .options(selectinload(ChatSchema.messages))
        .where(ChatSchema.id == chat_id, ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    return chat


async def delete_chat(db: AsyncSession, user_id: int, chat_id: int) -> bool:
    """Delete chat by id."""
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
