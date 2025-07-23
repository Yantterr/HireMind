from typing import Annotated

from fastapi import APIRouter, Depends, Request

import src.controllers.gpt_controllers as gpt_controllers
import src.dependencies.gpt_dependencies as gpt_dependencies
from src.dataclasses.gpt_dataclasses import ChatDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger
from src.models.gpt_models import (
    ChatCreateModel,
    ChatModel,
    ChatsModel,
    EventCreateModel,
    EventModel,
    MessageCreateModel,
)
from src.schemas import ChatSchema, EventSchema

gpt_router = APIRouter(
    prefix='/gpt',
    tags=['gpt'],
)


@gpt_router.get('/', response_model=list[ChatsModel])
async def chats_get_all(
    request: Request,
    db: SessionDep,
) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    user = request.state.user
    chats = await gpt_controllers.chats_get_all(user_id=user.id, db=db)

    return chats


@gpt_router.post('/', response_model=ChatModel)
async def chat_create(
    request: Request,
    db: SessionDep,
    redis: RedisDep,
    create_chat_data: ChatCreateModel,
) -> ChatDataclass:
    """Create a new GPT chat."""
    user = request.state.user
    chat = await gpt_controllers.chat_create(
        db=db, redis=redis, create_chat_data=create_chat_data, user_id=user.id, user_role=user.role
    )

    return chat


@gpt_router.delete('/{chat_id}', response_model=ChatModel)
async def chat_delete(
    request: Request,
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    user = request.state.user
    chat = await gpt_controllers.chat_delete(user_id=user.id, redis=redis, chat_id=chat_id, db=db)

    return chat


@gpt_router.post('/{chat_id}/messages', response_model=ChatModel)
async def message_create(
    create_message_data: MessageCreateModel,
    redis: RedisDep,
    db: SessionDep,
    chat: Annotated[ChatDataclass, Depends(gpt_dependencies.get_chat)],
) -> ChatDataclass:
    """Create and send message to GPT chat."""
    chat = await gpt_controllers.message_send(chat=chat, create_message_data=create_message_data, db=db, redis=redis)

    return chat


@gpt_router.post('/event', response_model=EventModel)
async def event_create(
    request: Request,
    event_create_data: EventCreateModel,
    db: SessionDep,
) -> EventSchema:
    """Create a new GPT event."""
    user = request.state.user
    if user.role != 'admin':
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    event = await gpt_controllers.event_create(db=db, event_create_data=event_create_data)

    return event


@gpt_router.get('/event', response_model=list[EventModel])
async def event_get_all(db: SessionDep) -> list[EventSchema]:
    """Get all GPT events."""
    events = await gpt_controllers.event_get_all(db=db)

    return events


@gpt_router.get('/{chat_id}', response_model=ChatModel)
async def chat_get(chat: Annotated[ChatDataclass, Depends(gpt_dependencies.get_chat)]) -> ChatDataclass:
    """Get GPT chat by ID."""
    return chat
