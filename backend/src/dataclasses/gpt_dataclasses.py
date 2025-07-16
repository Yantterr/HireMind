from dataclasses import dataclass
from typing import Optional

from src.dataclasses.generally_dataclasses import BaseDataclass
from src.models.generally_models import NNRoleEnum


@dataclass
class EventDataclass(BaseDataclass):
    """Event dataclass."""

    id: int
    content: str


@dataclass
class MessageDataclass(BaseDataclass):
    """User dataclass."""

    id: Optional[int]
    chat_id: int
    role: NNRoleEnum
    content: str
    created_at: str


@dataclass
class ChatDataclass(BaseDataclass):
    """User dataclass."""

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


@dataclass
class NNResponseDataclass(BaseDataclass):
    """User dataclass."""

    count_request_tokens: int
    count_response_tokens: int
    role: NNRoleEnum
    content: str
