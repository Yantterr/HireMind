from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request

import src.controllers.chats_controllers as chats_controllers
import src.dependencies.chats_dependencies as chats_dependencies
import src.utils.chats_utils as chats_utils
from src.dataclasses.chats_dataclasses import ChatDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger
from src.models.chats_models import (
    ChatCreateModel,
    ChatModel,
    ChatsModel,
    EventCreateModel,
    EventModel,
    MessageCreateModel,
)
from src.schemas import ChatSchema, EventSchema

chats_router = APIRouter(
    prefix='/chats',
    tags=['chats'],
)


@chats_router.get('/', response_model=list[ChatsModel])
async def chats_get_all(
    request: Request,
    db: SessionDep,
) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    user = request.state.user
    chats = await chats_controllers.chats_get_all(user_id=user.id, db=db)

    return chats


@chats_router.post('/', response_model=ChatModel)
async def chat_create(
    request: Request,
    db: SessionDep,
    redis: RedisDep,
    create_chat_data: ChatCreateModel,
) -> ChatDataclass:
    """Create a new GPT chat."""
    user = request.state.user
    chat = await chats_controllers.chat_create(
        db=db, redis=redis, create_chat_data=create_chat_data, user_id=user.id, user_role=user.role
    )

    return chat


@chats_router.delete('/{chat_id}', response_model=ChatModel)
async def chat_delete(
    request: Request,
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    user = request.state.user
    chat = await chats_controllers.chat_delete(user_id=user.id, redis=redis, chat_id=chat_id, db=db)

    return chat


@chats_router.put('/{chat_id}/messages', response_model=ChatModel)
async def message_create(
    create_message_data: MessageCreateModel,
    redis: RedisDep,
    db: SessionDep,
    chat: Annotated[ChatDataclass, Depends(chats_dependencies.get_chat)],
    background_tasks: BackgroundTasks,
) -> ChatDataclass:
    """Create and send message to GPT chat."""
    queue_position = await chats_utils.queue_add_task(redis=redis, chat_id=chat.id, user_id=chat.user_id)
    background_tasks.add_task(
        chats_controllers.message_send, chat=chat, create_message_data=create_message_data, db=db, redis=redis
    )

    chat.queue_position = queue_position
    return chat


@chats_router.post('/event', response_model=EventModel)
async def event_create(
    request: Request,
    event_create_data: EventCreateModel,
    db: SessionDep,
) -> EventSchema:
    """Create a new GPT event."""
    user = request.state.user
    if user.role != 'admin':
        raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    event = await chats_controllers.event_create(db=db, event_create_data=event_create_data)

    return event


@chats_router.get('/event', response_model=list[EventModel])
async def event_get_all(db: SessionDep) -> list[EventSchema]:
    """Get all GPT events."""
    events = await chats_controllers.event_get_all(db=db)

    return events


@chats_router.get('/{chat_id}', response_model=ChatModel)
async def chat_get(chat: Annotated[ChatDataclass, Depends(chats_dependencies.get_chat)]) -> ChatDataclass:
    """Get GPT chat by ID."""
    return chat
