from dataclasses import asdict
from json import dumps, loads

from fastapi import Request

import src.services.gpt_services as gpt_service
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

    chat = await gpt_service.chat_get(db=db, chat_id=chat_id)

    if not chat:
        raise Logger.create_response_error(error_key='data_not_found')

    await redis.set(name=f'notifications/delete={user_id}/chat:{chat_id}', value='', expire=3500)
    await redis.set(
        name=f'{user_id}/chat:{chat.id}',
        value=dumps(asdict(ChatDataclass.from_orm(chat))),
        expire=3600,
    )

    return ChatDataclass.from_orm(chat)
