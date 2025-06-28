from sqlalchemy import select

from src.database import AsyncSession
from src.gpt.models import chat_model
from src.schemas import ChatSchema


async def create_chat(db: AsyncSession, title: str, context: str, user_id: int) -> chat_model:
    """Create gpt chat."""
    print(title)
    new_chat = ChatSchema(user_id=user_id, context=context, title=title)

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    return new_chat


async def get_all_chats(user_id: int, db: AsyncSession) -> list[ChatSchema]:
    """Get all chats by user id."""
    request = select(
        ChatSchema.id, ChatSchema.title, ChatSchema.created_at, ChatSchema.updated_at, ChatSchema.is_archived
    ).where(ChatSchema.user_id == user_id, ~ChatSchema.is_archived)
    result = await db.execute(request)
    chats = result.mappings().all()

    print(chats)

    return chats


async def get_chat_by_id(chat_id: int, user_id: int, db: AsyncSession) -> ChatSchema | None:
    """Get chat by id."""
    request = select(ChatSchema).where(
        ChatSchema.id == chat_id, ChatSchema.user_id == user_id, ~ChatSchema.is_archived
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
