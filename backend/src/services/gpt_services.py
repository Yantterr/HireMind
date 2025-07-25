from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from src.dataclasses.gpt_dataclasses import EventDataclass
from src.logger import Logger
from src.models.generally_models import NNRoleEnum
from src.schemas import ChatSchema, EventSchema, MessageSchema


async def chat_get_all(db: AsyncSession, user_id: int) -> list[ChatSchema]:
    """Get all non-archived chats from database."""
    request = (
        select(ChatSchema)
        .where(and_(ChatSchema.user_id == user_id, ~ChatSchema.is_archived))
        .options(noload(ChatSchema.messages))
    )
    result = await db.execute(request)
    chats = result.scalars().all()

    return list(chats)


async def chat_get(db: AsyncSession, chat_id: int) -> Optional[ChatSchema]:
    """Get a non-archived chat by ID."""
    request = (
        select(ChatSchema)
        .where(ChatSchema.id == chat_id, ~ChatSchema.is_archived)
        .options(selectinload(ChatSchema.messages))
        .options(selectinload(ChatSchema.events))
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    return chat


async def chat_create(
    db: AsyncSession, title: str, event_chance: float, events: list[EventSchema], progression_type: int, user_id: int
) -> ChatSchema:
    """Create a new GPT chat with optional title."""
    new_chat = ChatSchema(
        user_id=user_id,
        title=title,
        events=events,
        progression_type=progression_type,
        current_event_chance=event_chance,
    )

    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat, attribute_names=['messages'])

    return new_chat


async def chat_edit(
    db: AsyncSession,
    chat_id: int,
    count_request_tokens: Optional[int] = None,
    count_response_tokens: Optional[int] = None,
    updated_at: Optional[datetime] = None,
    current_event_chance: Optional[float] = None,
    is_archived: Optional[bool] = None,
    events: Optional[list[EventDataclass]] = None,
    title: Optional[str] = None,
) -> ChatSchema:
    """Edit GPT chat by ID."""
    request = (
        select(ChatSchema)
        .where(ChatSchema.id == chat_id, ~ChatSchema.is_archived)
        .options(selectinload(ChatSchema.messages))
    )
    result = await db.execute(request)
    chat = result.scalars().first()

    if not chat:
        raise Logger.create_response_error(error_key='data_not_found')

    if current_event_chance is not None:
        chat.current_event_chance = current_event_chance
    if updated_at:
        chat.updated_at = updated_at
    if count_request_tokens:
        chat.count_request_tokens = count_request_tokens
    if count_response_tokens:
        chat.count_response_tokens = count_response_tokens
    if title:
        chat.title = title
    if is_archived is not None:
        chat.is_archived = is_archived

    if events:
        event_ids = [event.id for event in events]
        current_event_ids = {e.id for e in chat.events}
        new_event_ids = set(event_ids) - current_event_ids

        if new_event_ids:
            new_events_request = select(EventSchema).where(EventSchema.id.in_(new_event_ids))
            new_events_result = await db.execute(new_events_request)
            new_events = new_events_result.scalars().all()

            chat.events.extend(new_events)

    await db.commit()
    await db.refresh(chat)

    return chat


async def chat_count(
    db: AsyncSession,
    user_id: int,
) -> int:
    """Count the number of all chats for a user."""
    stmt = select(func.count()).select_from(ChatSchema).where(ChatSchema.user_id == user_id)
    result = await db.execute(stmt)
    count = result.scalar_one()
    return count


async def message_create(db: AsyncSession, chat_id: int, role: NNRoleEnum, content: str) -> MessageSchema:
    """Create a new message in the chat."""
    new_message = MessageSchema(chat_id=chat_id, role=role, content=content)

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message


async def event_create(db: AsyncSession, content: str) -> EventSchema:
    """Create a new event in the chat."""
    new_event = EventSchema(content=content)

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event


async def event_get_all(db: AsyncSession) -> list[EventSchema]:
    """Get all events from database."""
    request = select(EventSchema)
    result = await db.execute(request)
    events = result.scalars().all()

    return list(events)


async def event_get_random(db: AsyncSession, count: int) -> list[EventSchema]:
    """Get some amount random events."""
    random_func = func.random()
    request = select(EventSchema).order_by(random_func).limit(count)
    result = await db.execute(request)
    events = result.scalars().all()

    return list(events)


async def event_get_one(db: AsyncSession, exceptions: list[int]) -> Optional[EventSchema]:
    """Get some amount random events."""
    random_func = func.random()
    request = select(EventSchema).where(EventSchema.id.notin_(exceptions)).limit(1).order_by(random_func)
    result = await db.execute(request)
    event = result.scalars().first()

    return event
