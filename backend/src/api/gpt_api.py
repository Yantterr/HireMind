from typing import Annotated

from fastapi import APIRouter, Depends

import src.controllers.gpt_controllers as gpt_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.dependencies.gpt_dependencies as gpt_dependencies
from src.database import SessionDep
from src.dataclasses.auth_dataclasses import AuthDataclass
from src.dataclasses.gpt_dataclasses import ChatDataclass
from src.logger import Logger
from src.models.gpt_models import ChatCreateModel, ChatModel, EventCreateModel, EventModel, MessageCreateModel
from src.redis import RedisDep
from src.schemas import ChatSchema, EventSchema

gpt_router = APIRouter(
    prefix='/gpt',
    tags=['gpt'],
)


@gpt_router.get('/', response_model=list[ChatModel])
async def chats_get_all(
    db: SessionDep, auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)]
) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    chats = await gpt_controllers.chats_get_all(user_id=auth_data.user.id, db=db)

    return chats


@gpt_router.post('/', response_model=ChatModel)
async def chat_create(
    db: SessionDep,
    redis: RedisDep,
    create_chat_data: ChatCreateModel,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> ChatDataclass:
    """Create a new GPT chat."""
    chat = await gpt_controllers.chat_create(
        db=db, redis=redis, create_chat_data=create_chat_data, user_id=auth_data.user.id, user_role=auth_data.user.role
    )

    return chat


@gpt_router.delete('/{chat_id}', response_model=ChatModel)
async def chat_delete(
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    chat = await gpt_controllers.chat_delete(user_id=auth_data.user.id, redis=redis, chat_id=chat_id, db=db)

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
    event_create_data: EventCreateModel,
    db: SessionDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> EventSchema:
    """Create a new GPT event."""
    if auth_data.user.role != 'admin':
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
