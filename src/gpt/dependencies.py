from json import dumps, loads

from sqlalchemy.ext.asyncio import AsyncSession

import src.gpt.service as gpt_service
from src.database import AsyncRedis
from src.gpt.models import NNMessage_model, create_chat_model
from src.logger import Logger
from src.models import message_model
from src.schemas import ChatSchema
from src.users.dependencies import authorize_user


async def create_chat(
    create_chat_data: create_chat_model, token: str, user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> message_model:
    """Create gpt chat."""
    user_id = (await authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id

    chat = await gpt_service.create_chat(db=db, context=dumps([{}]), title=create_chat_data.title, user_id=user_id)

    await redis.hset(str(user_id), chat.id, chat.context)

    return message_model(message='Chat created successfully.')


async def get_all_chats(token: str, user_agent: str, redis: AsyncRedis, db: AsyncSession) -> list[ChatSchema]:
    """Get all user chats."""
    user_id = (await authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id

    chats = await gpt_service.get_all_chats(db=db, user_id=user_id)

    return chats


async def get_chat_by_id(chat_id: int, token: str, user_agent: str, redis: AsyncRedis, db: AsyncSession) -> ChatSchema:
    """Get chat by id."""
    user_id = (await authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id

    chat = await gpt_service.get_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)

    if chat is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    return chat


async def delete_chat(chat_id: int, token: str, user_agent: str, redis: AsyncRedis, db: AsyncSession) -> message_model:
    """Delete chat by id."""
    user_id = (await authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id

    res = await gpt_service.delete_chat(db=db, user_id=user_id, chat_id=chat_id)

    if not res:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    return message_model(message='Chat deleted successfully.')


async def send_message(
    chat_id: int, message: NNMessage_model, token: str, user_agent: str, redis: AsyncRedis, db: AsyncSession
) -> message_model:
    """Send message to gpt chat."""
    user_id = (await authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id
    chat_id_str = str(chat_id)

    old_contexts = await redis.hgetall(chat_id_str)

    if chat_id_str not in old_contexts:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    old_context = loads(old_contexts[chat_id_str])

    print(old_context)
