from datetime import datetime
from json import loads

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.schemas import ChatSchema, MessageSchema


async def save_expired_chat(message: dict, session_factory: async_sessionmaker[AsyncSession], redis: Redis):
    """Save expired chat."""
    chat = loads(await redis.get(message['data'].split('=')[1]))

    async with session_factory() as session:
        try:
            objs = [
                MessageSchema(
                    created_at=datetime.fromisoformat(msg['created_at']),
                    content=msg['content'],
                    role=msg['role'],
                    chat_id=chat['id'],
                )
                for msg in chat['messages']
                if msg['id'] is None
            ]

            session.add_all(objs)
            await session.commit()
        except Exception as e:
            print(f'Error processing expired key in DB: {e}')
        finally:
            await session.close()
