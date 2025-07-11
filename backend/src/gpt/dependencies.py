from datetime import datetime
from json import dumps, loads
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import src.gpt.service as gpt_service
import src.gpt.utils as gpt_utils
import src.utils as generally_utils
from src.config import NNConfig
from src.gpt.dataclassees import Chat, Message
from src.gpt.engine import create_gpt_request
from src.gpt.models import ChatCreateModel, ChatModel, MessageCreateModel
from src.logger import Logger
from src.models import MessageModel
from src.redis import AsyncRedis
from src.schemas import ChatSchema


async def create_chat(
    create_chat_data: ChatCreateModel,
    token: Optional[str],
    hash: Optional[str],
    user_agent: str,
    redis: AsyncRedis,
    db: AsyncSession,
) -> ChatSchema:
    """Create gpt chat."""
    response = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

    user_id, role = response.user_id, response.role

    if role == 'anonymous':
        count_chats = await gpt_service.get_count_chats(db=db, user_id=user_id, is_archived=False)
        if count_chats >= 1:
            raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    system_prompt_content = (
        f'Вы собеседуете кандидата на позицию {NNConfig["language"][create_chat_data.language]} разработчика. '
        f'{NNConfig["difficulty"][create_chat_data.difficulty]} '
        f'{NNConfig["politeness"][create_chat_data.politeness]} '
        f'{NNConfig["friendliness"][create_chat_data.friendliness]} '
        f'{NNConfig["rigidity"][create_chat_data.rigidity]} '
        f'{NNConfig["detail_orientation"][create_chat_data.detail_orientation]} '
        f'{NNConfig["pacing"][create_chat_data.pacing]}'
    )

    chat = await gpt_service.create_chat(db=db, title=create_chat_data.title, user_id=user_id)

    messages = await gpt_service.create_message(db=db, chat_id=chat.id, role='system', content=system_prompt_content)

    chat.messages.append(messages)

    await redis.set(name=f'{user_id}/chat:{chat.id}', value=dumps(chat), expire=2000)
    await redis.set(name=f'notifications/delete={user_id}/chat:{chat.id}', value='', expire=1990)

    return chat


async def get_all_chats(
    token: Optional[str], hash: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> list[ChatSchema]:
    """Get all user chats."""
    user_id = (
        await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)
    ).user_id

    chats = await gpt_service.get_all_chats(db=db, user_id=user_id)

    return chats


async def get_chat_by_id(
    chat_id: int, token: Optional[str], hash: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> ChatSchema:
    """Get chat by id."""
    user_id = (
        await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)
    ).user_id

    redis_chat = await redis.get(value=f'{user_id}/chat:{chat_id}')
    if redis_chat is not None:
        return loads(redis_chat)

    chat = await gpt_service.get_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)

    if chat is None:
        raise Logger.create_response_error(error_key='data_not_found')

    await redis.set(name=f'{user_id}/chat:{chat.id}', value=ChatModel.model_validate(chat).model_dump_json(), expire=2)

    return chat


async def delete_chat(
    chat_id: int, token: Optional[str], hash: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> MessageModel:
    """Delete chat by id."""
    user_id = (
        await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)
    ).user_id

    await redis.delete(f'{user_id}/chat:{chat_id}')

    res = await gpt_service.delete_chat(db=db, user_id=user_id, chat_id=chat_id)

    if not res:
        raise Logger.create_response_error(error_key='data_not_found')

    return MessageModel(message='Chat deleted successfully.')


async def send_message(
    chat_id: int,
    message: MessageCreateModel,
    token: Optional[str],
    hash: Optional[str],
    user_agent: str,
    redis: AsyncRedis,
    db: AsyncSession,
) -> Chat:
    """Send message to gpt chat."""
    user_id = (
        await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)
    ).user_id

    chat = await gpt_utils.get_chat(db=db, user_id=user_id, redis=redis, chat_id=chat_id)

    chat.messages.append(
        Message(
            role=message.role,
            content=message.content,
            created_at=datetime.now(),
            chat_id=chat.id,
            id=None,
        )
    )

    gpt_response = create_gpt_request(chat=chat)

    chat.messages.append(
        Message(
            id=None, role='assistant', content=gpt_response.result, created_at=gpt_response.created_at, chat_id=chat.id
        )
    )

    chat.count_request_tokens += gpt_response.request_tokens
    chat.count_response_tokens += gpt_response.response_tokens

    await redis.set(name=f'{user_id}/chat:{chat_id}', value=dumps(chat), expire=2000)
    await redis.set(name=f'notifications/delete={user_id}/chat:{chat_id}', value='', expire=1990)

    return chat
