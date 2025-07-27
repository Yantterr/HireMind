from dataclasses import asdict
from json import dumps, loads

from fastapi import Request

import src.services.gpt_services as gpt_service
import src.utils.gpt_utils as gpt_utils
from src.config import settings
from src.dataclasses.gpt_dataclasses import ChatDataclass
from src.engines.database_engine import SessionDep
from src.engines.redis_engine import RedisDep
from src.logger import Logger


async def get_chat(
    request: Request,
    chat_id: int,
    db: SessionDep,
    redis: RedisDep,
) -> ChatDataclass:
    """Get GPT chat by ID."""
    user = request.state.user
    user_id = user.id
    redis_chat = await redis.get(value=f'{user_id}/chat:{chat_id}')
    if redis_chat:
        chat = loads(redis_chat)
        return ChatDataclass.from_dict(chat)

    chat = await gpt_service.chat_get(db=db, user_id=user_id, chat_id=chat_id)
    if not chat:
        raise Logger.create_response_error(error_key='data_not_found')

    chat_dataclass = ChatDataclass.from_orm(chat)
    queue_position = await gpt_utils.queue_get_position(redis=redis, chat_id=chat_id)
    chat_dataclass.queue_position = queue_position

    await gpt_utils.chat_save(chat=chat_dataclass, redis=redis)

    return chat_dataclass
