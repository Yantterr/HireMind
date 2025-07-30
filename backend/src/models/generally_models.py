from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


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


T = TypeVar('T')


class PaginationParamsModel(BaseModel):
    """Pagination parameters for API requests."""

    page: int = Field(1, ge=1, description='Page number')
    per_page: int = Field(10, ge=1, le=100, description='Items per page')


class PaginatedResponseModel(BaseModel, Generic[T]):
    """Standard API response containing a list of items and pagination metadata."""

    items: list[T]
    page: int
    per_page: int
    total_items: int
    total_pages: int


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
