from enum import StrEnum

from pydantic import BaseModel


class Base(BaseModel):
    """Base model with config pydantic for sqlalchemy."""

    model_config = {'from_attributes': True, 'use_enum_values': True}


class MessageModel(Base):
    """Model with message field."""

    message: str


class RoleEnum(StrEnum):
    """Role enum."""

    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
