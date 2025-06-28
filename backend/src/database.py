from typing import Annotated, AsyncGenerator, Awaitable

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

redis_client: Redis | None = None
engine = create_async_engine(settings.database_url)

session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
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


async def close_redis() -> None:
    """Close redis connect."""
    global redis_client
    if redis_client:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()


class AsyncRedis:
    """Async performance of redis."""

    def __init__(self, redis_engine: Redis):
        self.redis_engine = redis_engine

    def exists(self, value: str) -> Awaitable[bool]:
        """Async version of exists."""
        result = self.redis_engine.exists(value)
        assert isinstance(result, Awaitable)
        return result

    def hgetall(self, name: str) -> Awaitable[dict[str, str]]:
        """Async version of hgetall."""
        result = self.redis_engine.hgetall(name=name)
        assert isinstance(result, Awaitable)
        return result

    def delete(self, value: str) -> Awaitable[bool]:
        """Async version of delete."""
        result = self.redis_engine.delete(value)
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
