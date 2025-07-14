from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.dataclasses.generally_dataclasses import BaseDataclass
from src.models.generally_models import NNRoleEnum


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
    title: str
    messages: list[MessageDataclass]
    is_archived: bool
    count_request_tokens: int
    count_response_tokens: int
    created_at: str
    updated_at: str
