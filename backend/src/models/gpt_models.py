from datetime import datetime
from typing import Optional

from pydantic import Field

from src.models.generally_models import Base, NNRoleEnum


class MessageModel(Base):
    """Response model containing a message string."""

    id: int
    role: NNRoleEnum
    content: str
    created_at: datetime


class ChatModel(Base):
    """Model for retrieving chat details."""

    id: int
    title: str
    is_archived: bool
    messages: list[MessageModel]
    count_request_tokens: int
    count_response_tokens: int
    created_at: datetime
    updated_at: datetime


class ChatCreateModel(Base):
    """Model for creating a chat with optional title."""

    title: str
    role: NNRoleEnum

    difficulty: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    politeness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    friendliness: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    rigidity: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    detail_orientation: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    pacing: int = Field(ge=0, le=4, description='Value must be between 0 and 4 inclusive.')
    language: int = Field(
        ge=0, le=9, description='Value must be between 0 and 9 inclusive. Represents the programming language used.'
    )
