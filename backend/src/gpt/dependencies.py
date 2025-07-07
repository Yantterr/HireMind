from datetime import datetime
from json import dumps, loads
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

import src.gpt.service as gpt_service
import src.utils as generally_utils
from src.database import AsyncRedis
from src.gpt.engine import create_gpt_request
from src.gpt.models import ChatCreateModel, ChatModel, MessageCreateModel
from src.logger import Logger
from src.models import MessageModel
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
    user_id = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

    chat = await gpt_service.create_chat(db=db, title=create_chat_data.title, user_id=user_id)

    await redis.set(
        name=f'{user_id}/chat:{chat.id}',
        value=ChatModel.model_validate(chat).model_dump_json(),
        expire=2_592_000,
    )

    return chat


async def get_all_chats(
    token: Optional[str], hash: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> list[ChatSchema]:
    """Get all user chats."""
    user_id = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

    chats = await gpt_service.get_all_chats(db=db, user_id=user_id)

    return chats


async def get_chat_by_id(
    chat_id: int, token: Optional[str], hash: Optional[str], user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> ChatSchema:
    """Get chat by id."""
    user_id = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

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
    user_id = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

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
) -> ChatModel:
    """Send message to gpt chat."""
    user_id = await generally_utils.get_user_id(token=token, hash=hash, db=db, user_agent=user_agent, redis=redis)

    json_chat = await redis.get(value=f'{user_id}/chat:{chat_id}')

    if json_chat is None:
        chat = await gpt_service.get_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)

        if chat is None:
            raise Logger.create_response_error(error_key='data_not_found')

        json_chat = ChatModel.model_validate(chat).model_dump_json()

    chat = loads(json_chat)

    chat['messages'].append({**message.model_dump(), 'created_at': datetime.now().isoformat(timespec='seconds')})

    chat['messages'].sort(key=lambda msg: msg['created_at'])

    gpt_response = create_gpt_request(chat=chat)

    chat['messages'].append(
        {'id': None, 'role': 'assistant', 'content': gpt_response.result, 'created_at': gpt_response.created_at}
    )

    chat['count_request_tokens'] += gpt_response.request_tokens
    chat['count_response_tokens'] += gpt_response.response_tokens

    await redis.set(name=f'{user_id}/chat:{chat_id}', value=dumps(chat), expire=2000)
    await redis.set(name=f'notifications/delete={user_id}/chat:{chat_id}', value='', expire=1990)

    return ChatModel(**chat)
