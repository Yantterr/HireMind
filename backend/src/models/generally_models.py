from enum import StrEnum

from pydantic import BaseModel


class Base(BaseModel):
    """Base model configuration.

    This configuration includes:
    - ORM mode
    - Enum value serialization
    - Strict input validation
    """

    model_config = {'from_attributes': True, 'use_enum_values': True, 'extra': 'forbid'}


class ResponseModel(Base):
    """Standard API response containing a message string."""

    message: str


class NNRoleEnum(StrEnum):
    """Defines participant roles in neural network interactions."""

    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class SystemRoleEnum(StrEnum):
    """Defines access levels within the application ecosystem."""

    ADMIN = 'admin'
    USER = 'user'
    ANONYM = 'anonym'
