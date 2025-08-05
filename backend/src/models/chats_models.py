from datetime import datetime
from typing import Optional

from pydantic import Field

from src.models.generally_models import Base, NNRoleEnum, PaginatedResponseModel

RATING_FIELD = Field(ge=0, le=4, description='Rating scale from 0 to 4 inclusive')
LANGUAGE_FIELD = Field(ge=0, le=9, description='Programming language identifier (0-9 inclusive)')
PROGRESSION_FIELD = Field(ge=0, le=1, description='0: arithmetic progression, 1: geometric progression')


class MessageModel(Base):
    """Individual message within a chat conversation."""

    id: Optional[int] = None
    role: NNRoleEnum
    content: str
    created_at: datetime


class EventModel(Base):
    """Significant event occurring within a chat session."""

    id: int
    content: str


class EventPaginatedModel(PaginatedResponseModel[EventModel]):
    """Model for paginated list of events."""

    pass


class ChatUserModel(Base):
    """Complete chat session with metadata and content."""

    id: int
    title: str
    messages: list[MessageModel]
    events: list[EventModel]
    created_at: datetime
    updated_at: datetime
    queue_position: int


class ChatsUserModel(Base):
    """Minimal chat representation for listing purposes."""

    id: int
    title: str
    updated_at: datetime


class ChatAdminModel(ChatUserModel):
    """Complete chat session with metadata and content."""

    current_event_chance: float
    progression_type: int
    is_archived: bool
    total_count_request_tokens: int
    total_count_response_tokens: int
    current_count_request_tokens: int


class ChatsAdminModel(PaginatedResponseModel[ChatAdminModel]):
    """Complete chat session with metadata and content."""

    pass


class ChatCreateModel(Base):
    """Parameters for initializing a new chat session."""

    title: str
    initial_context: Optional[str] = None
    progression_type: int = PROGRESSION_FIELD
    difficulty: int = RATING_FIELD
    politeness: int = RATING_FIELD
    friendliness: int = RATING_FIELD
    rigidity: int = RATING_FIELD
    detail_orientation: int = RATING_FIELD
    pacing: int = RATING_FIELD
    language: int = LANGUAGE_FIELD


class MessageCreateModel(Base):
    """Payload for adding a new message to a chat."""

    role: NNRoleEnum
    content: str


class EventCreateModel(Base):
    """Payload for recording a chat event."""

    content: str


class NNResponseModel(Base):
    """AI-generated response with token usage metrics."""

    count_request_tokens: int
    count_response_tokens: int
    role: NNRoleEnum
    content: str
