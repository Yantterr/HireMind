from datetime import datetime

from pydantic import Field

from src.models.generally_models import Base, NNRoleEnum


class MessageModel(Base):
    """Response model containing a message string."""

    id: int | None
    role: NNRoleEnum
    content: str
    created_at: datetime


class EventModel(Base):
    """Response model containing a chat event."""

    id: int
    content: str


class ChatModel(Base):
    """Model for retrieving chat details."""

    id: int
    title: str
    is_archived: bool
    messages: list[MessageModel]
    events: list[EventModel]
    count_request_tokens: int
    count_response_tokens: int
    current_event_chance: float
    created_at: datetime
    updated_at: datetime


class ChatsModel(Base):
    """Model for retrieving list of chats."""

    id: int
    title: str
    is_archived: bool
    count_request_tokens: int
    count_response_tokens: int
    created_at: datetime
    updated_at: datetime


class ChatCreateModel(Base):
    """Model for creating a chat with optional title."""

    title: str

    progression_type: int = Field(
        ge=0,
        le=1,
        description='Value must be between 0 and 1 inclusive. 0 - arithmetic progression, 1 - geometric progression.',
    )

    difficulty: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    politeness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    friendliness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    rigidity: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    detail_orientation: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    pacing: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    language: int = Field(
        ge=0, le=9, description='Value must be between 0 and 9 inclusive. Represents the programming language used.'
    )


class MessageCreateModel(Base):
    """Model for creating a message."""

    role: NNRoleEnum
    content: str


class EventCreateModel(Base):
    """Model for create a event."""

    content: str


class NNResponseModel(Base):
    """Response model containing a message string."""

    count_request_tokens: int
    count_response_tokens: int
    role: NNRoleEnum
    content: str
