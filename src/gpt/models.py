from datetime import datetime
from typing import Literal, Optional

from src.models import base_model
from src.users.models import user_model


class NNResponse_model(base_model):
    """Neural network response."""

    request_tokens: int
    response_tokens: int
    message: str
    result: str


class NNMessage_model(base_model):
    """Neural network message."""

    role: Literal['system', 'user', 'assistant']
    content: str


class NNContext_model(base_model):
    """Neural network context."""

    messages: list[NNMessage_model]


class base_chat_model(base_model):
    """Base chat model."""

    pass


class create_chat_model(base_chat_model):
    """Create chat model."""

    title: Optional[str]


class get_chat_model(create_chat_model):
    """Get chat model."""

    id: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class get_chats_model(base_chat_model):
    """Get chats model."""

    chats: list[get_chat_model]


class chat_model(base_model):
    """Chat model."""

    user_id: int
    context: NNContext_model
    user: user_model
