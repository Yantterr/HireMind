from datetime import datetime
from json import loads
from typing import Annotated, Awaitable, Optional

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import src.services.gpt_services as gpt_service
import src.utils.gpt_utils as gpt_utils
from src.config import settings
from src.dataclasses.gpt_dataclasses import ChatDataclass
from src.engines.database_engine import session_factory

redis_client: Redis | None = None


async def init_redis() -> None:
    """Initialization the Redis client connection with parameters from settings."""
    global redis_client
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password.get_secret_value(),
        decode_responses=True,
    )
    await redis_client.ping()
    await redis_client.config_set('notify-keyspace-events', 'Ex')


async def close_redis() -> None:
    """Close redis client connect."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()


async def listen_redis_chat_expired() -> None:
    """Listen for Redis key expiration events.

    When a key matching pattern 'notifications/delete=' expires, it triggers the "save_expired_chat" handler.
    """
    global redis_client
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
            await gpt_utils.save_messages(chat=chat, db=session)
            await gpt_service.chat_edit(
                db=session,
                chat_id=chat.id,
                events=chat.events,
                count_request_tokens=chat.count_request_tokens,
                count_response_tokens=chat.count_response_tokens,
                updated_at=datetime.fromisoformat(chat.updated_at),
                current_event_chance=chat.current_event_chance,
            )
            await session.close()

    except Exception as e:
        print(f'Error processing expired key in DB: {e}')


class AsyncRedis:
    """Wrapper class to provide async Redis operations with type Awaitable."""

    def __init__(self, redis_engine: Redis):
        self.redis_engine = redis_engine

    def exists(self, value: str) -> Awaitable[bool]:
        """Check asynchronously if a key exists in Redis."""
        result = self.redis_engine.exists(value)
        assert isinstance(result, Awaitable)
        return result

    def delete(self, *value: str) -> Awaitable[bool]:
        """Delete asynchronously keys in Redis."""
        result = self.redis_engine.delete(*value)
        assert isinstance(result, Awaitable)
        return result

    def get(self, value: str) -> Awaitable[Optional[str]]:
        """Get asynchronously a key from Redis."""
        result = self.redis_engine.get(value)
        assert isinstance(result, Awaitable)
        return result

    def set(self, name: str, value: str, expire: int) -> Awaitable[str]:
        """Set asynchronously a key in Redis."""
        result = self.redis_engine.set(name=name, value=value, ex=expire)
        assert isinstance(result, Awaitable)
        return result

    def keys(self, pattern: str) -> Awaitable[list[str]]:
        """Get asynchronously all keys matching a pattern in Redis."""
        result = self.redis_engine.keys(pattern)
        assert isinstance(result, Awaitable)
        return result


def get_redis() -> AsyncRedis:
    """Get async Redis client."""
    if redis_client is None:
        raise RuntimeError('Redis client is not initialized')
    return AsyncRedis(redis_client)


RedisDep = Annotated[AsyncRedis, Depends(get_redis)]
