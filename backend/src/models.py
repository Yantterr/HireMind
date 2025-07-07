from enum import StrEnum

from pydantic import BaseModel


class Base(BaseModel):
    """Base Pydantic model with ORM and enum value support."""

    model_config = {'from_attributes': True, 'use_enum_values': True, 'extra': 'forbid'}


class MessageModel(Base):
    """Response model containing a message string."""

    message: str


class NNRoleEnum(StrEnum):
    """Roles for neural network participants."""

    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class SystemRoleEnum(StrEnum):
    """System user roles."""

    ADMIN = 'admin'
    USER = 'user'
    ANONYM = 'anonym'
