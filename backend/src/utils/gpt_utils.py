from sqlalchemy.ext.asyncio import AsyncSession

from src.dataclasses.gpt_dataclasses import ChatDataclass, MessageDataclass
from src.schemas import MessageSchema


async def save_messages(chat: ChatDataclass, db: AsyncSession) -> ChatDataclass:
    """Save messages from redis to the database and return updated chat."""
    new_messages = []
    indexes = []

    for i, message in enumerate(chat.messages):
        if message.id is None:
            new_messages.append(
                MessageSchema(
                    created_at=message.created_at,
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
