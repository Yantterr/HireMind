from fastapi import APIRouter, Request

import src.gpt.dependencies as gpt_dep
from src.database import RedisDep, SessionDep
from src.gpt.models import NNMessage_model, chat_model, create_chat_model, get_chats_model
from src.models import message_model

gpt_router = APIRouter(
    prefix='/gpt',
    tags=['gpt'],
)


@gpt_router.get('/', response_model=get_chats_model)
async def get_all_chats(request: Request, redis: RedisDep, db: SessionDep) -> get_chats_model:
    """Get all gpt chats."""
    user_agent = request.headers.get('user-agent')
    token = request.cookies.get('token')
    all_chats = await gpt_dep.get_all_chats(redis=redis, db=db, token=token, user_agent=user_agent)

    return all_chats


@gpt_router.post('/', response_model=message_model)
async def create_chat(
    create_chat_data: create_chat_model, request: Request, redis: RedisDep, db: SessionDep
) -> message_model:
    """Create gpt chat."""
    token = request.cookies.get('token')
    user_agent = request.headers.get('user-agent')
    res = await gpt_dep.create_chat(
        token=token, create_chat_data=create_chat_data, user_agent=user_agent, redis=redis, db=db
    )
    return res


@gpt_router.get('/{chat_id}', response_model=chat_model)
async def get_chat(request: Request, redis: RedisDep, db: SessionDep) -> get_chats_model:
    """Get gpt chat by id."""
    user_agent = request.headers.get('user-agent')
    token = request.cookies.get('token')
    chat_id = int(request.path_params['chat_id'])
    chat = await gpt_dep.get_chat_by_id(chat_id=chat_id, token=token, user_agent=user_agent, redis=redis, db=db)
    return chat


@gpt_router.delete('/{chat_id}', response_model=message_model)
async def delete_chat(request: Request, redis: RedisDep, db: SessionDep) -> message_model:
    """Delete gpt chat by id."""
    user_agent = request.headers.get('user-agent')
    token = request.cookies.get('token')
    chat_id = int(request.path_params['chat_id'])
    res = await gpt_dep.delete_chat_by_id(chat_id=chat_id, token=token, user_agent=user_agent, redis=redis, db=db)
    return res


@gpt_router.put('/{chat_id}', response_model=message_model)
async def update_chat(request: Request, message: NNMessage_model, redis: RedisDep, db: SessionDep) -> message_model:
    """Update gpt chat by id."""
    user_agent = request.headers.get('user-agent')
    token = request.cookies.get('token')
    chat_id = int(request.path_params['chat_id'])
    res = await gpt_dep.send_message(
        chat_id=chat_id, message=message, token=token, user_agent=user_agent, redis=redis, db=db
    )
    return res
