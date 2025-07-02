from json import loads


async def save_expired_chat(message: dict, redis: Redis):
    """Save expired chat."""
    print(message)
    if message['type'] == 'pmessage':
        if message['data'].startswith('notifications/delete='):
            chat = loads(await redis.get(message['data'].split('=')[1]))
            async with session_factory() as session:
                try:
                    objs = [
                        ChatSchema(
                            **msg,
                        )
                        for msg in chat['messages']
                        if msg['id'] is not None
                    ]

                    print(objs)

                    session.add_all(objs)
                    await session.commit()

                except Exception as e:
                    print(f'Error processing expired key in DB: {e}')
                finally:
                    await session.close()
