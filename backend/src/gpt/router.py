from fastapi import APIRouter, Request

import src.gpt.dependencies as gpt_dep
import src.utils as generally_utils
from src.database import RedisDep, SessionDep
from src.gpt.models import ChatCreateModel, ChatGetModel, ChatModel, MessageCreateModel
from src.models import MessageModel
from src.schemas import ChatSchema

gpt_router = APIRouter(
    prefix='/gpt',
    tags=['gpt'],
)


@gpt_router.get('/', response_model=list[ChatGetModel])
async def get_all_chats(request: Request, redis: RedisDep, db: SessionDep) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)
    all_chats = await gpt_dep.get_all_chats(redis=redis, db=db, token=token, hash=hash, user_agent=user_agent)
    return all_chats


@gpt_router.post('/', response_model=ChatModel)
async def create_chat(
    create_chat_data: ChatCreateModel, request: Request, redis: RedisDep, db: SessionDep
) -> ChatSchema:
    """Create a new GPT chat."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)
    res = await gpt_dep.create_chat(
        token=token, hash=hash, create_chat_data=create_chat_data, user_agent=user_agent, redis=redis, db=db
    )
    return res


@gpt_router.get('/{chat_id}', response_model=ChatModel)
async def get_chat(request: Request, redis: RedisDep, db: SessionDep) -> ChatSchema:
    """Get GPT chat by ID."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)
    chat_id = int(request.path_params['chat_id'])
    chat = await gpt_dep.get_chat_by_id(
        chat_id=chat_id, token=token, hash=hash, user_agent=user_agent, redis=redis, db=db
    )
    return chat


@gpt_router.delete('/{chat_id}', response_model=MessageModel)
async def delete_chat(request: Request, redis: RedisDep, db: SessionDep, chat_id: int) -> MessageModel:
    """Delete GPT chat by ID (soft delete)."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)
    res = await gpt_dep.delete_chat(chat_id=chat_id, hash=hash, token=token, user_agent=user_agent, redis=redis, db=db)
    return res


@gpt_router.post('/{chat_id}/messages', response_model=ChatModel)
async def update_chat(
    request: Request, message: MessageCreateModel, redis: RedisDep, db: SessionDep, chat_id: int
) -> ChatModel:
    """Add a message to GPT chat by ID."""
    token, hash, user_agent = await generally_utils.get_authorization_data(request=request)
    res = await gpt_dep.send_message(
        chat_id=chat_id, message=message, db=db, token=token, hash=hash, user_agent=user_agent, redis=redis
    )
    return res
