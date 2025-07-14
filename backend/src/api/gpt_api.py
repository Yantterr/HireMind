from typing import Annotated

from fastapi import APIRouter, Depends

import src.controllers.gpt_controllers as gpt_controllers
import src.dependencies.auth_dependencies as auth_dependencies
from src.database import SessionDep
from src.dataclasses.auth_dataclasses import AuthDataclass
from src.dataclasses.gpt_dataclasses import ChatDataclass
from src.models.gpt_models import ChatCreateModel, ChatModel
from src.redis import RedisDep
from src.schemas import ChatSchema

gpt_router = APIRouter(
    prefix='/gpt',
    tags=['gpt'],
)


@gpt_router.get('/', response_model=list[ChatModel])
async def all_chats(
    db: SessionDep, auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)]
) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    chats = await gpt_controllers.get_all_chats(user_id=auth_data.user.id, db=db)

    return chats


@gpt_router.get('/{chat_id}', response_model=ChatModel)
async def get_chat(
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> ChatDataclass:
    """Get GPT chat by ID."""
    chat = await gpt_controllers.get_chat(user_id=auth_data.user.id, redis=redis, chat_id=chat_id, db=db)

    return chat


@gpt_router.post('/', response_model=ChatModel)
async def create_chat(
    db: SessionDep,
    redis: RedisDep,
    create_chat_data: ChatCreateModel,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> ChatDataclass:
    """Create a new GPT chat."""
    chat = await gpt_controllers.create_chat(
        db=db, redis=redis, create_chat_data=create_chat_data, user_id=auth_data.user.id
    )

    return chat


@gpt_router.delete('/{chat_id}', response_model=ChatModel)
async def delete_chat(
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
    auth_data: Annotated[AuthDataclass, Depends(auth_dependencies.get_current_user)],
) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    chat = await gpt_controllers.delete_chat(user_id=auth_data.user.id, redis=redis, chat_id=chat_id, db=db)

    return chat
