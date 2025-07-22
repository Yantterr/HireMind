from datetime import datetime
from secrets import choice
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import src.services.gpt_services as gpt_service
from src.dataclasses.gpt_dataclasses import ChatDataclass, MessageDataclass, NNResponseDataclass
from src.models.generally_models import NNRoleEnum
from src.schemas import EventSchema, MessageSchema


async def save_messages(chat: ChatDataclass, db: AsyncSession) -> ChatDataclass:
    """Save messages from redis to the database and return updated chat."""
    new_messages = []
    indexes = []

    for i, message in enumerate(chat.messages):
        if message.id is None:
            new_messages.append(
                MessageSchema(
                    created_at=datetime.fromisoformat(message.created_at),
                    content=message.content,
                    role=message.role,
                    chat_id=chat.id,
                )
            )
            indexes.append(i)

    if len(new_messages) == 0:
        return chat

    db.add_all(new_messages)
    await db.commit()

    for i, new_msg in zip(indexes, new_messages):
        updated_message = MessageDataclass(
            id=new_msg.id,
            chat_id=new_msg.chat_id,
            created_at=new_msg.created_at,
            content=new_msg.content,
            role=new_msg.role,
        )
        chat.messages[i] = updated_message

    return chat


async def event_get_random(db: AsyncSession) -> list[EventSchema]:
    """GPT Util for get random event."""
    count = int(choice([0, 1, 2, 3]))
    events = await gpt_service.event_get_random(db=db, count=count)

    return events


async def event_get_one(db: AsyncSession, chat: ChatDataclass) -> tuple[Optional[EventSchema], float]:
    """GPT Util for get random event."""
    if chat.progression_type == 1:
        new_percent = chat.current_event_chance + 10.0
    elif chat.progression_type == 0:
        new_percent = chat.current_event_chance * 1.6

    if choice(range(1, 100)) <= new_percent:
        event = await gpt_service.event_get_one(db=db, exceptions=[event.id for event in chat.events])

        if chat.progression_type == 0:
            return event, 1.5
        else:
            return event, 10.0

    else:
        return None, new_percent


async def NNRequest(context: list[MessageDataclass]) -> NNResponseDataclass:
    """Make a request to NN."""
    return NNResponseDataclass(
        role=NNRoleEnum.ASSISTANT, content='Hello!', count_request_tokens=1, count_response_tokens=1
    )
