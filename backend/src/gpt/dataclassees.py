from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Message dataclass."""

    id: Optional[int]
    role: str
    content: str
    created_at: datetime
    chat_id: int


@dataclass
class Chat:
    """Chat dataclass."""

    id: int
    user_id: int
    messages: list[Message]

    count_request_tokens: int
    count_response_tokens: int


@dataclass
class GptResponse:
    """GPT response dataclass."""

    request_tokens: int
    response_tokens: int
    result: str
    created_at: datetime
