from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from src.logger import Logger
from src.schemas import ChatSchema, MessageSchema


async def get_all_chats(db: AsyncSession, user_id: int) -> list[ChatSchema]:
    """Get all non-archived chats from database."""
    request = (
        select(ChatSchema)
        .where(ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
        .options(noload(ChatSchema.messages))
    )
    result = await db.execute(request)
    chats = result.scalars().all()

    return list(chats)


async def get_chat(db: AsyncSession, chat_id: int) -> Optional[ChatSchema]:
    """Get a non-archived chat by ID."""
    request = (
        select(ChatSchema)
        .where(ChatSchema.id == chat_id, ~ChatSchema.is_archived)
        .options(selectinload(ChatSchema.messages))
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    return chat


async def create_chat(db: AsyncSession, title: str, user_id: int) -> ChatSchema:
    """Create a new GPT chat with optional title."""
    new_chat = ChatSchema(user_id=user_id, title=title)

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat, attribute_names=['messages'])

    return new_chat


async def edit_chat(
    db: AsyncSession, chat_id: int, user_id: int, is_archived: Optional[bool] = None, title: Optional[str] = None
) -> ChatSchema:
    """Edit GPT chat by ID."""
    request = (
        select(ChatSchema)
        .where(ChatSchema.id == chat_id, ~ChatSchema.is_archived, ChatSchema.user_id == user_id)
        .options(selectinload(ChatSchema.messages))
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    if not chat:
        raise Logger.create_response_error(error_key='data_not_found')

    if title:
        chat.title = title

    if is_archived is not None:
        chat.is_archived = is_archived

    await db.commit()
    await db.refresh(chat)

    return chat


async def count_chats(
    db: AsyncSession,
    user_id: int,
) -> int:
    """Count the number of all chats for a user."""
    stmt = select(func.count()).select_from(ChatSchema).where(ChatSchema.user_id == user_id)
    result = await db.execute(stmt)
    count = result.scalar_one()
    return count


async def create_message(db: AsyncSession, chat_id: int, role: str, content: str) -> MessageSchema:
    """Create a new message in the chat."""
    new_message = MessageSchema(chat_id=chat_id, role=role, content=content)

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message
