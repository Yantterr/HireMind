from dataclasses import asdict
from datetime import datetime
from json import dumps, loads

from sqlalchemy.ext.asyncio import AsyncSession

import src.engines.ollama_engine as ollama_engine
import src.services.gpt_services as gpt_service
import src.utils.gpt_utils as gpt_utils
from src.config import NNConfig
from src.dataclasses.gpt_dataclasses import ChatDataclass, EventDataclass, MessageDataclass
from src.engines.redis_engine import AsyncRedis
from src.logger import Logger
from src.models.generally_models import NNRoleEnum, SystemRoleEnum
from src.models.gpt_models import ChatCreateModel, EventCreateModel, MessageCreateModel
from src.schemas import ChatSchema, EventSchema


async def chats_get_all(db: AsyncSession, user_id: int) -> list[ChatSchema]:
    """Get all GPT chats for the authorized user."""
    chats = await gpt_service.chat_get_all(user_id=user_id, db=db)

    return chats


async def chat_create(
    db: AsyncSession, redis: AsyncRedis, create_chat_data: ChatCreateModel, user_id: int, user_role: SystemRoleEnum
) -> ChatDataclass:
    """Create a new GPT chat."""
    if user_role == SystemRoleEnum.ANONYM:
        count_chats = await gpt_service.chat_count(
            db=db,
            user_id=user_id,
        )
        if count_chats >= 1:
            raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

    events = await gpt_utils.event_get_random(db=db)

    system_prompt_content = (
        f'Вы собеседуете кандидата на позицию {NNConfig["language"][create_chat_data.language]} разработчика. '
        f"""Имитируй живого человека, который помогает подготовиться к собеседованию.
        Начни с короткого дружелюбного приветствия (1 предложение).
        Задавай строго по одному вопросу за раз, даже если ответ пользователя будет односложным ("да"/"нет").
        Всегда дожидайся ответа перед следующим вопросом.
        Держи реплики краткими (максимум 2 предложения).
        Активно слушай: используй уточнения и естественные реакции на ответы."""
        f"""Имитируйте поведение обычного человека, вопросы задавай по очереди и начинай с
        небольшого дружелюбного диалога для подготовки к собеседованию. Твои реплики должны быть не слишком длинные и
        не задавай много вопросов подряд. Задавай новые вопросы по мере ответа на старые,
        даже если ответ будет односложным типо: да или нет, то все равно жди ответа и не задавай новый вопрос."""
        f'{NNConfig["difficulty"][create_chat_data.difficulty]} '
        f'{NNConfig["politeness"][create_chat_data.politeness]} '
        f'{NNConfig["friendliness"][create_chat_data.friendliness]} '
        f'{NNConfig["rigidity"][create_chat_data.rigidity]} '
        f'{NNConfig["detail_orientation"][create_chat_data.detail_orientation]} '
        f'{NNConfig["pacing"][create_chat_data.pacing]}'
    ) + ' '.join(event.content for event in events)

    event_chance = 1.5 if create_chat_data.progression_type == 0 else 10.0
    chat = await gpt_service.chat_create(
        db=db,
        events=events,
        event_chance=event_chance,
        progression_type=create_chat_data.progression_type,
        title=create_chat_data.title,
        user_id=user_id,
    )
    message = await gpt_service.message_create(
        db=db, chat_id=chat.id, role=NNRoleEnum.SYSTEM, content=system_prompt_content
    )

    chat_dataclass = ChatDataclass.from_orm(chat)
    chat_dataclass.messages.append(MessageDataclass.from_orm(message))

    nn_response = await ollama_engine.ollama_request(messages=chat_dataclass.messages)

    chat_dataclass.messages.append(
        MessageDataclass(
            id=None,
            chat_id=chat_dataclass.id,
            role=NNRoleEnum.ASSISTANT,
            content=nn_response.content,
            created_at=datetime.now().isoformat(),
        )
    )

    await redis.set(name=f'notifications/delete={user_id}/chat:{chat.id}', value='', expire=5)
    await redis.set(name=f'{user_id}/chat:{chat.id}', value=dumps(asdict(chat_dataclass)), expire=10)

    return chat_dataclass


async def chat_delete(chat_id: int, user_id: int, db: AsyncSession, redis: AsyncRedis) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    chat = await gpt_service.chat_edit(db=db, is_archived=True, chat_id=chat_id)

    redis_chat = await redis.get(f'{user_id}/chat:{chat_id}')
    if redis_chat:
        chat_dict = loads(redis_chat)
        chat_dataclass = ChatDataclass.from_dict(chat_dict)

        chat = await gpt_utils.save_messages(chat=chat_dataclass, db=db)

        await redis.delete(f'notifications/delete={user_id}/chat:{chat_id}')
        await redis.delete(f'{user_id}/chat:{chat_id}')
    else:
        chat = ChatDataclass.from_orm(chat)

    return chat


async def message_send(
    chat: ChatDataclass, create_message_data: MessageCreateModel, redis: AsyncRedis, db: AsyncSession
) -> ChatDataclass:
    """Create and send message to GPT chat."""
    chat.messages.append(
        MessageDataclass(
            id=None,
            chat_id=chat.id,
            role=create_message_data.role,
            content=create_message_data.content,
            created_at=datetime.now().isoformat(),
        )
    )

    random_event, new_percent = await gpt_utils.event_get_one(db=db, chat=chat)
    if random_event:
        chat.events.append(EventDataclass.from_orm(random_event))
        chat.messages.append(
            MessageDataclass(
                id=None,
                chat_id=chat.id,
                role=NNRoleEnum.SYSTEM,
                content='Событие добавлено: ' + random_event.content,
                created_at=datetime.now().isoformat(),
            )
        )

    chat.current_event_chance = new_percent

    nn_response = await ollama_engine.ollama_request(messages=chat.messages)
    chat.count_request_tokens += nn_response.count_request_tokens
    chat.count_response_tokens += nn_response.count_response_tokens
    chat.messages.append(
        MessageDataclass(
            id=None,
            chat_id=chat.id,
            role=NNRoleEnum.ASSISTANT,
            content=nn_response.content,
            created_at=datetime.now().isoformat(),
        )
    )

    await redis.set(name=f'notifications/delete={chat.user_id}/chat:{chat.id}', value='', expire=5)
    await redis.set(
        name=f'{chat.user_id}/chat:{chat.id}',
        value=dumps(asdict(chat)),
        expire=10,
    )

    chat.updated_at = datetime.now().isoformat()

    return chat


async def event_create(event_create_data: EventCreateModel, db: AsyncSession) -> EventSchema:
    """Create a new event."""
    new_event = await gpt_service.event_create(db=db, content=event_create_data.content)

    return new_event


async def event_get_all(db: AsyncSession) -> list[EventSchema]:
    """Get all events."""
    events = await gpt_service.event_get_all(db=db)

    return events
