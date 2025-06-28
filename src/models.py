from enum import StrEnum

from pydantic import BaseModel


class base_model(BaseModel):
    """Base model with config pydantic for sqlalchemy."""

    model_config = {'from_attributes': True}


class message_model(base_model):
    """Model with message field."""

    message: str


class RoleEnum(StrEnum):
    """Role enum."""

    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
