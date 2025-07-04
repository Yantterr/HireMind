from datetime import datetime
from json import loads

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.schemas import MessageSchema


async def save_expired_chat(message: dict, session_factory: async_sessionmaker[AsyncSession], redis: Redis):
    """Save new messages from expired Redis chat data to the database."""
    try:
        key = message['data'].split('=')[1]
        chat_data_json = await redis.get(key)
        if not chat_data_json:
            print(f'No chat data found in Redis for key: {key}')
            return

        chat = loads(chat_data_json)

        objs = [
            MessageSchema(
                created_at=datetime.fromisoformat(msg['created_at']),
                content=msg['content'],
                role=msg['role'],
                chat_id=chat['id'],
            )
            for msg in chat['messages']
            if msg.get('id') is None
        ]

        async with session_factory() as session:
            session.add_all(objs)
            await session.commit()

    except Exception as e:
        print(f'Error processing expired key in DB: {e}')
