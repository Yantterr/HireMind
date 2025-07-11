from datetime import datetime
from typing import Optional

from pydantic import Field

from src.models import Base, NNRoleEnum


class MessageBaseModel(Base):
    """Base message model with optional ID, role, and content."""

    id: Optional[int] = None
    role: NNRoleEnum
    content: str


class MessageCreateModel(MessageBaseModel):
    """Model for creating a message."""

    pass


class MessageGetModel(MessageCreateModel):
    """Model for retrieving a message with creation timestamp."""

    created_at: datetime


class ChatBaseModel(Base):
    """Base chat model."""

    pass


class ChatCreateModel(ChatBaseModel):
    """Model for creating a chat with optional title."""

    title: Optional[str]

    difficulty: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    politeness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    friendliness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    rigidity: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    detail_orientation: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    pacing: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    language: int = Field(
        ge=0, le=9, description='Value must be between 0 and 9 inclusive. Represents the programming language used.'
    )


class ChatGetModel(ChatCreateModel):
    """Model for retrieving chat details."""

    id: int
    is_archived: bool
    count_request_tokens: int
    count_response_tokens: int
    created_at: datetime
    updated_at: datetime


class ChatModel(ChatGetModel):
    """Full chat model including user ID and optional messages."""

    user_id: int
    messages: Optional[list[MessageGetModel]]
