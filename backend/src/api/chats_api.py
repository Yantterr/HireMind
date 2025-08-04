from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

import src.controllers.chats_controllers as chats_controllers
import src.dependencies.auth_dependencies as auth_dependencies
import src.dependencies.chats_dependencies as chats_dependencies
import src.dependencies.generally_dependencies as generally_dependencies
import src.utils.chats_utils as chats_utils
from src.dto.chats_dto import ChatDataclass
from src.dto.users_dto import UserDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.models.chats_models import (
    ChatCreateModel,
    ChatModel,
    ChatsModel,
    MessageCreateModel,
)
from src.models.generally_models import PaginatedResponseModel, PaginationParamsModel

chats_router = APIRouter(
    prefix='/chats',
    tags=['chats'],
)


@chats_router.get('/', response_model=PaginatedResponseModel[ChatsModel])
async def chats_get_all(
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('anonym'))],
    pagination_params: Annotated[PaginationParamsModel, Depends(generally_dependencies.get_pagination_params)],
    db: SessionDep,
) -> PaginatedResponseModel[ChatsModel]:
    """Get all GPT chats."""
    chats, page, per_page, total_items, total_pages = await chats_controllers.chats_get_all(
        user_id=user.id, page=pagination_params.page, per_page=pagination_params.per_page, role=user.role, db=db
    )

    return PaginatedResponseModel(
        items=[ChatsModel.model_validate(chat) for chat in chats],
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
    )


@chats_router.post('/', response_model=ChatModel)
async def chat_create(
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('anonym'))],
    db: SessionDep,
    redis: RedisDep,
    create_chat_data: ChatCreateModel,
) -> ChatDataclass:
    """Create a new GPT chat."""
    chat = await chats_controllers.chat_create(
        db=db, redis=redis, create_chat_data=create_chat_data, user_id=user.id, user_role=user.role
    )

    return chat


@chats_router.delete('/{chat_id}', response_model=ChatModel)
async def chat_delete(
    user: Annotated[UserDataclass, Depends(auth_dependencies.require_permission('anonym'))],
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
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
    await chats_utils.chat_save(chat=chat, redis=redis)
    return chat


@chats_router.get('/{chat_id}', response_model=ChatModel)
async def chat_get(chat: Annotated[ChatDataclass, Depends(chats_dependencies.get_chat)]) -> ChatDataclass:
    """Get GPT chat by ID."""
    return chat
