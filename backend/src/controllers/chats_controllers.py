from datetime import datetime
from json import loads

from sqlalchemy.ext.asyncio import AsyncSession

import src.engines.ollama_engine as ollama_engine
import src.services.chats_services as gpt_service
import src.utils.chats_utils as chats_utils
import src.utils.redis_utils as redis_utils
from src.config import NNConfig
from src.dataclasses.chats_dataclasses import ChatDataclass, EventDataclass, MessageDataclass
from src.engines.redis_engine import AsyncRedis
from src.logger import Logger
from src.models.chats_models import ChatCreateModel, EventCreateModel, MessageCreateModel
from src.models.generally_models import NNRoleEnum, SystemRoleEnum
from src.schemas import ChatSchema, EventSchema


async def chats_get_all(
    db: AsyncSession, per_page: int, page: int, role: SystemRoleEnum, user_id: int
) -> tuple[list[ChatSchema], int, int, int, int]:
    """Get all GPT chats for the authorized user."""
    filter_user_id = None if role == SystemRoleEnum.ADMIN else user_id

    return await gpt_service.chat_get_all(db=db, user_id=filter_user_id, per_page=per_page, page=page)


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

    if create_chat_data.initial_context:
        initial_context = await chats_utils.ollama_generate_initial_context(create_chat_data.initial_context)
    else:
        initial_context = ''

    events = await chats_utils.event_get_random(db=db)

    system_prompt_content = (
        f'Ты — живой интервьюер с уникальной личностью, проводящий собеседование на позицию '
        f'{NNConfig["language"][create_chat_data.language]} разработчика.'
        'Критически важно соблюдать естественный диалоговый ритм:\n\n'
        'ЖЕСТКИЕ ПРАВИЛА ДИАЛОГА:\n'
        '1. Первое сообщение: ТОЛЬКО приветствие и представление (1-2 предложения)\n'
        "   Пример: 'Привет! Я Алексей, senior-разработчик. Рад видеть тебя на собеседовании.'\n"
        '2. После приветствия ОБЯЗАТЕЛЬНО ДОЖДИСЬ ответа кандидата\n'
        '3. Только после ответа задай ПЕРВЫЙ вопрос\n'
        '4. Всегда задавай строго по одному вопросу за реплику\n'
        '5. Между вопросами ВСЕГДА жди ответа пользователя\n'
        '6. Реплики должны быть краткими (1-2 предложения максимум)\n\n'
        'ТЕХНИКИ ЕСТЕСТВЕННОГО ПОВЕДЕНИЯ:\n'
        '- После ответа кандидата делай микропаузу (0.5-2 сек)\n'
        "- Используй подтверждающие реплики ('Понял', 'Интересно')\n"
        '- Задавай уточняющие вопросы по ответам\n'
        "- Проявляй эмоциональные реакции ('О, необычный подход!')\n"
        "- Допускай естественные паузы обдумывания ('Дай-ка подумать...')\n\n"
        'СТРУКТУРА СОБЕСЕДОВАНИЯ:\n'
        '1. Приветствие (только в первом сообщении)\n'
        '2. Легкий разогревочный вопрос\n'
        '3. Технические вопросы по вакансии\n'
        '4. Поведенческие вопросы\n'
        '5. Вопросы кандидату\n\n'
        'ПАРАМЕТРЫ СТИЛЯ:\n'
        f'• Сложность: {NNConfig["difficulty"][create_chat_data.difficulty]}\n'
        f'• Вежливость: {NNConfig["politeness"][create_chat_data.politeness]}\n'
        f'• Дружелюбие: {NNConfig["friendliness"][create_chat_data.friendliness]}\n'
        f'• Жёсткость: {NNConfig["rigidity"][create_chat_data.rigidity]}\n'
        f'• Детализация: {NNConfig["detail_orientation"][create_chat_data.detail_orientation]}\n'
        f'• Темп: {NNConfig["pacing"][create_chat_data.pacing]}\n\n'
        f'КОНТЕКСТ ВАКАНСИИ:\n{initial_context}\n\n'
        'ДОПОЛНИТЕЛЬНЫЕ СОБЫТИЯ:\n' + '\n'.join(f'- {event.content}' for event in events) + '\n\n'
        'ЗАПРЕЩЕНО:\n'
        '- Задавать несколько вопросов подряд\n'
        '- Продолжать без ответа пользователя\n'
        '- Делать длинные монологи\n'
        '- Использовать шаблонные фразы\n'
    )
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

    await chats_utils.chat_save(chat=ChatDataclass.from_orm(chat), redis=redis)

    return chat_dataclass


async def chat_delete(chat_id: int, user_id: int, db: AsyncSession, redis: AsyncRedis) -> ChatDataclass:
    """Delete GPT chat by ID (soft delete)."""
    chat = await gpt_service.chat_edit(db=db, is_archived=True, chat_id=chat_id)

    redis_chat = await redis.get(f'{user_id}/chat:{chat_id}')
    if redis_chat:
        chat_dict = loads(redis_chat)
        chat_dataclass = ChatDataclass.from_dict(chat_dict)

        chat = await redis_utils.save_messages(chat=chat_dataclass, db=db)

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

    random_event, new_percent = await chats_utils.event_get_one(db=db, chat=chat)
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
    await chats_utils.queue_remove_task(redis=redis)

    chat.queue_position = 0
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

    await chats_utils.chat_save(chat=chat, redis=redis)
    chat.updated_at = datetime.now().isoformat()

    return chat


async def event_create(event_create_data: EventCreateModel, db: AsyncSession) -> EventSchema:
    """Create a new event."""
    new_event = await gpt_service.event_create(db=db, content=event_create_data.content)

    return new_event


async def event_get_all(db: AsyncSession, page: int, per_page: int) -> tuple[list[EventSchema], int, int, int, int]:
    """Get all events."""
    return await gpt_service.event_get_all(db=db, page=page, per_page=per_page)
