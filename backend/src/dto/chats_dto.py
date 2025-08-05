from dataclasses import dataclass
from typing import Optional

from src.dto.generally_dto import BaseDataclass, PaginatedDataclass
from src.models.generally_models import NNRoleEnum


@dataclass
class EventDataclass(BaseDataclass):
    """Event dataclass."""

    id: int
    content: str


@dataclass
class MessageDataclass(BaseDataclass):
    """Message dataclass."""

    id: Optional[int]
    chat_id: int
    role: NNRoleEnum
    content: str
    created_at: str


@dataclass
class ChatDataclass(BaseDataclass):
    """Chat dataclass."""

    id: int
    user_id: int
    title: str
    messages: list[MessageDataclass]
    current_event_chance: float
    progression_type: int
    events: list[EventDataclass]
    is_archived: bool
    total_count_request_tokens: int
    total_count_response_tokens: int
    current_count_request_tokens: int
    created_at: str
    updated_at: str
    queue_position: Optional[int] = 0


@dataclass
class ChatsAdminDataclass(BaseDataclass):
    """Chats dataclass."""

    id: int
    user_id: int
    title: str
    current_event_chance: float
    progression_type: int
    is_archived: bool
    total_count_request_tokens: int
    total_count_response_tokens: int
    current_count_request_tokens: int
    created_at: str
    updated_at: str
    queue_position: Optional[int]


@dataclass
class ChatsUserDataclass(BaseDataclass):
    """Chats dataclass."""

    id: int
    title: str
    updated_at: str


@dataclass
class ChatsAdminPaginatedDataclass(PaginatedDataclass[ChatsAdminDataclass]):
    """Chats dataclass with pagination."""

    pass


@dataclass
class EventsPaginatedDataclass(PaginatedDataclass[EventDataclass]):
    """Events dataclass with pagination."""

    pass


@dataclass
class NNResponseDataclass(BaseDataclass):
    """Neural Network response."""

    count_request_tokens: int
    count_response_tokens: int
    role: NNRoleEnum
    content: str


@dataclass
class NNQueueCellDataclass(BaseDataclass):
    """Neural Network cell in queue."""

    chat_id: int
    user_id: int


@dataclass
class NNQueueDataclass(BaseDataclass):
    """Neural Network queue dataclass."""

    cells: list[NNQueueCellDataclass]
