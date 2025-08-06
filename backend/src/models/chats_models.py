from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.generally_models import NNRoleEnum, PaginatedResponseModel

RATING_FIELD = Field(ge=0, le=4, description='Rating scale from 0 to 4 inclusive')
LANGUAGE_FIELD = Field(ge=0, le=9, description='Programming language identifier (0-9 inclusive)')
PROGRESSION_FIELD = Field(ge=0, le=1, description='0: arithmetic progression, 1: geometric progression')


class MessageBase(BaseModel):
    """Base message model."""

    content: str


class EventBase(BaseModel):
    """Base event model."""

    content: str


class ChatBase(BaseModel):
    """Base chat model."""

    title: str
    created_at: datetime
    updated_at: datetime


class MessageModel(MessageBase):
    """Individual message within a chat conversation."""

    id: Optional[int] = None
    role: NNRoleEnum
    created_at: datetime


class EventModel(EventBase):
    """Significant event occurring within a chat session."""

    id: int


class EventPaginatedModel(PaginatedResponseModel):
    """Model for paginated list of events."""

    items: List[EventModel]


class ChatCoreModel(ChatBase):
    """Core chat model with common fields."""

    messages: List[MessageModel]
    events: List[EventModel]


class ChatUserModel(ChatCoreModel):
    """Complete chat session with metadata and content."""

    id: int
    queue_position: int


class ChatAdminModel(ChatUserModel):
    """Complete chat session with admin-specific metadata."""

    current_event_chance: float
    progression_type: int
    is_archived: bool
    total_count_request_tokens: int
    total_count_response_tokens: int
    current_count_request_tokens: int


class ChatsUserModel(BaseModel):
    """Minimal chat representation for listing purposes."""

    id: int
    title: str
    updated_at: datetime


class ChatsAdminModel(PaginatedResponseModel):
    """Paginated list of admin chats."""

    items: List[ChatAdminModel]


class ChatCreateModel(BaseModel):
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


class MessageCreateModel(MessageBase):
    """Payload for adding a new message to a chat."""

    role: NNRoleEnum


class EventCreateModel(EventBase):
    """Payload for recording a chat event."""


class NNResponseModel(MessageBase):
    """AI-generated response with token usage metrics."""

    count_request_tokens: int
    count_response_tokens: int
    role: NNRoleEnum
