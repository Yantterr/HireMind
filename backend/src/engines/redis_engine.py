from typing import Annotated, Awaitable, Optional

from fastapi import Depends
from redis.asyncio import Redis

from src.config import settings

redis_client: Redis | None = None


async def init_redis() -> Redis:
    """Initialization the Redis client connection with parameters from settings."""
    global redis_client
    redis_client = Redis(
        decode_responses=True,
        **settings.redis_settings,
    )
    await redis_client.ping()
    await redis_client.config_set('notify-keyspace-events', 'Ex')
    return redis_client


async def close_redis() -> None:
    """Close redis client connect."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()


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

    def set(self, name: str, value: str, expire: Optional[int] = None) -> Awaitable[str]:
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
