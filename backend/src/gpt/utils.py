from json import loads

from sqlalchemy.ext.asyncio import AsyncSession

import src.gpt.service as gpt_service
from src.gpt.dataclassees import Chat, Message
from src.logger import Logger
from src.redis import AsyncRedis


async def get_chat(user_id: int, chat_id: int, db: AsyncSession, redis: AsyncRedis) -> Chat:
    """Function to get chat data by id."""
    redis_chat = await redis.get(value=f'{user_id}/chat:{chat_id}')

    if redis_chat:
        chat = loads(redis_chat)
        return chat
    else:
        chat_schema = await gpt_service.get_chat_by_id(db=db, user_id=user_id, chat_id=chat_id)
        if not chat_schema:
            raise Logger.create_response_error(error_key='data_not_found')

        chat = Chat(
            id=chat_schema.id,
            user_id=chat_schema.user_id,
            count_request_tokens=chat_schema.count_request_tokens,
            count_response_tokens=chat_schema.count_response_tokens,
            messages=[
                Message(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                    chat_id=message.chat_id,
                )
                for message in chat_schema.messages
            ],
        )

        chat.messages.sort(key=lambda msg: msg.created_at)

        return chat
