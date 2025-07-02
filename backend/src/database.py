from typing import Annotated, AsyncGenerator, Awaitable, Optional

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.gpt.utils import save_expired_chat

redis_client: Redis | None = None
engine = create_async_engine(settings.database_url)

session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


class SqlalchemyBase(DeclarativeBase):
    """Base class for all sqlalchemy schemes."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get sqlalchemy session."""
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_redis() -> None:
    """Initialization redis."""
    global redis_client
    redis_client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
    )
    await redis_client.ping()
    await redis_client.config_set('notify-keyspace-events', 'Ex')


async def close_redis() -> None:
    """Close redis connect."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()


async def listen_redis_chat_expired() -> None:
    """Listen redis chat expired."""
    global redis_client
    if redis_client is None:
        raise RuntimeError('Redis client is not initialized')

    pubsub = redis_client.pubsub()
    await pubsub.psubscribe('__keyevent@0__:expired')
    async for message in pubsub.listen():
        print(message)
        await save_expired_chat(message=message, redis=redis_client)


class AsyncRedis:
    """Async performance of redis."""

    def __init__(self, redis_engine: Redis):
        self.redis_engine = redis_engine

    def exists(self, value: str) -> Awaitable[bool]:
        """Async version of exists."""
        result = self.redis_engine.exists(value)
        assert isinstance(result, Awaitable)
        return result

    def delete(self, *value: str) -> Awaitable[bool]:
        """Async version of delete."""
        result = self.redis_engine.delete(*value)
        assert isinstance(result, Awaitable)
        return result

    def get(self, value: str) -> Awaitable[Optional[str]]:
        """Async version of get."""
        result = self.redis_engine.get(value)
        assert isinstance(result, Awaitable)
        return result

    def set(self, name: str, value: str, expire: int) -> Awaitable[str]:
        """Async version of set."""
        result = self.redis_engine.set(name=name, value=value, ex=expire)
        assert isinstance(result, Awaitable)
        return result

    def keys(self, pattern: str) -> Awaitable[list[str]]:
        """Async version of keys."""
        result = self.redis_engine.keys(pattern)
        assert isinstance(result, Awaitable)
        return result

    def hexists(self, name: str, key: str) -> Awaitable[bool]:
        """Async version of hexists."""
        result = self.redis_engine.hexists(name=name, key=key)
        assert isinstance(result, Awaitable)
        return result

    def hexpire(self, name: str, field: str, time: int) -> Awaitable[bool]:
        """Async version of hexpire."""
        result = self.redis_engine.hexpire(name, time, field)
        assert isinstance(result, Awaitable)
        return result

    def hgetall(self, name: str) -> Awaitable[dict[str, str]]:
        """Async version of hgetall."""
        result = self.redis_engine.hgetall(name=name)
        assert isinstance(result, Awaitable)
        return result

    def hget(self, name: str, key: str) -> Awaitable[Optional[str]]:
        """Async version of hget."""
        result = self.redis_engine.hget(name=name, key=key)
        assert isinstance(result, Awaitable)
        return result

    def hset(self, name: str, key: str, value: str) -> Awaitable[int]:
        """Async version of hset."""
        result = self.redis_engine.hset(name=name, value=value, key=key)
        assert isinstance(result, Awaitable)
        return result

    def hdel(self, name: str, *keys: str) -> Awaitable[int]:
        """Async version of hdel."""
        result = self.redis_engine.hdel(name, *keys)
        assert isinstance(result, Awaitable)
        return result


def get_redis() -> AsyncRedis:
    """Get async redis."""
    if redis_client is None:
        raise RuntimeError('Redis client is not initialized')
    return AsyncRedis(redis_client)


SessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[AsyncRedis, Depends(get_redis)]
