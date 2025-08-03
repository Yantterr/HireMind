from dataclasses import dataclass
from typing import Optional

from src.dto.generally_dto import BaseDataclass
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
    count_request_tokens: int
    count_response_tokens: int
    created_at: str
    updated_at: str
    queue_position: Optional[int] = 0


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
