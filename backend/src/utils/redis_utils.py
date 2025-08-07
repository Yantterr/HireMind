from datetime import datetime
from json import loads

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import src.services.chats_services as gpt_service
from src.dto.chats_dto import ChatDataclass, MessageDataclass
from src.engines.database_engine import session_factory
from src.schemas import MessageSchema


async def save_messages(chat: ChatDataclass, db: AsyncSession) -> ChatDataclass:
    """Save messages from redis to the database and return updated chat."""
    new_messages = []
    indexes = []

    for i, message in enumerate(chat.messages):
        if message.id is None:
            new_messages.append(
                MessageSchema(
                    created_at=datetime.fromisoformat(message.created_at),
                    content=message.content,
                    role=message.role,
                    chat_id=chat.id,
                )
            )
            indexes.append(i)

    if len(new_messages) == 0:
        return chat

    db.add_all(new_messages)
    await db.commit()

    for i, new_msg in zip(indexes, new_messages):
        updated_message = MessageDataclass(
            id=new_msg.id,
            chat_id=new_msg.chat_id,
            created_at=new_msg.created_at,
            content=new_msg.content,
            role=new_msg.role,
        )
        chat.messages[i] = updated_message

    return chat


async def save_expired_chat(message: dict, session_factory: async_sessionmaker[AsyncSession], redis: Redis):
    """Save new messages from expired Redis chat data to the database."""
    try:
        key = message['data'].split('=')[1]
        chat_data_json = await redis.get(key)
        if not chat_data_json:
            print(f'No chat data found in Redis for key: {key}')
            return

        chat = ChatDataclass.from_dict(loads(chat_data_json))

        async with session_factory() as session:
            await save_messages(chat=chat, db=session)
            await gpt_service.chat_edit(
                db=session,
                chat_id=chat.id,
                events=chat.events,
                total_count_request_tokens=chat.total_count_request_tokens,
                total_count_response_tokens=chat.total_count_response_tokens,
                current_count_request_tokens=chat.current_count_request_tokens,
                updated_at=datetime.fromisoformat(chat.updated_at),
                current_event_chance=chat.current_event_chance,
            )
            await session.close()

    except Exception as e:
        print(f'Error processing expired key in DB: {e}')


async def listen_redis_chat_expired(redis_client: Redis) -> None:
    """Listen for Redis key expiration events.

    When a key matching pattern 'notifications/delete=' expires, it triggers the "save_expired_chat" handler.
    """
    if redis_client is None:
        raise RuntimeError('Redis client is not initialized')

    pubsub = redis_client.pubsub()
    await pubsub.psubscribe('__keyevent@0__:expired')
    async for message in pubsub.listen():
        if redis_client is None:
            raise RuntimeError('Redis client is not initialized')
        if message['type'] == 'pmessage':
            if message['data'].startswith('notifications/delete='):
                await save_expired_chat(message=message, session_factory=session_factory, redis=redis_client)
