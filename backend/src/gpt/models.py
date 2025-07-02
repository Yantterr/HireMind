from datetime import datetime
from typing import Optional

from src.models import Base, RoleEnum


class MessageBaseModel(Base):
    """Base message model."""

    id: int | None = None
    role: RoleEnum
    content: str


class MessageCreateModel(MessageBaseModel):
    """Create message model."""

    pass


class MessageGetModel(MessageCreateModel):
    """Get message model."""

    created_at: datetime


class GptResponseModel(Base):
    """Neural network response."""

    request_tokens: int
    response_tokens: int
    message: str
    result: str


class ChatBaseModel(Base):
    """Base chat model."""

    pass


class ChatCreateModel(ChatBaseModel):
    """Create chat model."""

    title: Optional[str]


class ChatGetModel(ChatCreateModel):
    """Get chat model."""

    id: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class ChatModel(ChatGetModel):
    """Chat model."""

    user_id: int
    messages: Optional[list[MessageGetModel]]
