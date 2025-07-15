from dataclasses import asdict
from json import dumps, loads

from sqlalchemy.ext.asyncio import AsyncSession

import src.services.gpt_services as gpt_service
import src.utils.gpt_utils as gpt_utils
from src.config import NNConfig
from src.dataclasses.gpt_dataclasses import ChatDataclass, MessageDataclass
from src.logger import Logger
from src.models.gpt_models import ChatCreateModel
from src.redis import AsyncRedis
from src.schemas import ChatSchema


async def get_all_chats(db: AsyncSession, user_id: int) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    chats = await gpt_service.get_all_chats(user_id=user_id, db=db)

    return chats


async def get_chat(user_id: int, chat_id: int, db: AsyncSession, redis: AsyncRedis) -> ChatDataclass:
    """Get GPT chat by ID."""
    redis_chat = await redis.get(value=f'{user_id}/chat:{chat_id}')
    if redis_chat:
        chat = loads(redis_chat)

        return ChatDataclass(
            id=chat['id'],
            title=chat['title'],
            is_archived=chat['is_archived'],
            count_request_tokens=chat['count_request_tokens'],
            count_response_tokens=chat['count_response_tokens'],
            created_at=chat['created_at'],
            updated_at=chat['updated_at'],
            messages=[MessageDataclass.from_dict(message) for message in chat['messages']],
        )

    chat = await gpt_service.get_chat(db=db, chat_id=chat_id)

    if not chat:
        raise Logger.create_response_error(error_key='data_not_found')

    await redis.set(
        name=f'{user_id}/chat:{chat.id}',
        value=dumps(
            asdict(
                ChatDataclass(
                    id=chat.id,
                    title=chat.title,
                    is_archived=chat.is_archived,
                    count_request_tokens=chat.count_request_tokens,
                    count_response_tokens=chat.count_response_tokens,
                    created_at=chat.created_at.isoformat(),
                    updated_at=chat.updated_at.isoformat(),
                    messages=[MessageDataclass.from_orm(message) for message in chat.messages],
                )
            )
        ),
        expire=3600,
    )

    return ChatDataclass.from_orm(chat)


async def create_chat(
    db: AsyncSession, redis: AsyncRedis, create_chat_data: ChatCreateModel, user_id: int
) -> ChatDataclass:
    """Create a new GPT chat."""
    if create_chat_data.role == 'anonymous':
        count_chats = await gpt_service.count_chats(
            db=db,
            user_id=user_id,
        )
        if count_chats >= 1:
            raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    system_prompt_content = (
        f'Вы собеседуете кандидата на позицию {NNConfig["language"][create_chat_data.language]} разработчика. '
        f'{NNConfig["difficulty"][create_chat_data.difficulty]} '
        f'{NNConfig["politeness"][create_chat_data.politeness]} '
        f'{NNConfig["friendliness"][create_chat_data.friendliness]} '
        f'{NNConfig["rigidity"][create_chat_data.rigidity]} '
        f'{NNConfig["detail_orientation"][create_chat_data.detail_orientation]} '
        f'{NNConfig["pacing"][create_chat_data.pacing]}'
    )

    chat = await gpt_service.create_chat(db=db, title=create_chat_data.title, user_id=user_id)
    message = await gpt_service.create_message(db=db, chat_id=chat.id, role='system', content=system_prompt_content)

    chat_dataclass = ChatDataclass(
        id=chat.id,
        title=chat.title,
        count_request_tokens=chat.count_request_tokens,
        count_response_tokens=chat.count_response_tokens,
        is_archived=chat.is_archived,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
        messages=[MessageDataclass.from_orm(message)],
    )

    await redis.set(name=f'{user_id}/chat:{chat.id}', value=dumps(asdict(chat_dataclass)), expire=2000)
    await redis.set(name=f'notifications/delete={user_id}/chat:{chat.id}', value='', expire=1990)

    return chat_dataclass


async def delete_chat(chat_id: int, user_id: int, db: AsyncSession, redis: AsyncRedis) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    chat = await gpt_service.edit_chat(db=db, user_id=user_id, is_archived=True, chat_id=chat_id)

    redis_chat = await redis.get(f'{user_id}/chat:{chat_id}')
    if redis_chat:
        chat_dict = loads(redis_chat)
        chat_dataclass = ChatDataclass(
            title=chat_dict['title'],
            id=chat_dict['id'],
            is_archived=chat_dict['is_archived'],
            count_request_tokens=chat_dict['count_request_tokens'],
            count_response_tokens=chat_dict['count_response_tokens'],
            messages=[MessageDataclass.from_dict(message) for message in chat_dict['messages']],
            created_at=chat_dict['created_at'],
            updated_at=chat_dict['updated_at'],
        )

        chat = await gpt_utils.save_messages(chat=chat_dataclass, db=db)

        await redis.delete(f'notifications/delete={user_id}/chat:{chat_id}')
        await redis.delete(f'{user_id}/chat:{chat_id}')
    else:
        chat = ChatDataclass(
            title=chat.title,
            id=chat.id,
            is_archived=chat.is_archived,
            count_request_tokens=chat.count_request_tokens,
            count_response_tokens=chat.count_response_tokens,
            messages=[MessageDataclass.from_orm(message) for message in chat.messages],
            created_at=chat.created_at.isoformat(),
            updated_at=chat.updated_at.isoformat(),
        )

    return chat
