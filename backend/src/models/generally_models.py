from enum import StrEnum
from re import compile
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

PASSWORD_DIGIT_PATTERN = compile(r'\d')
PASSWORD_UPPERCASE_PATTERN = compile(r'[A-Z]')
PASSWORD_LOWERCASE_PATTERN = compile(r'[a-z]')
PASSWORD_SPECIAL_PATTERN = compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]')


class Base(BaseModel):
    """Base model configuration.

    This configuration includes:
    - ORM mode
    - Enum value serialization
    - Strict input validation
    """

    model_config = {'from_attributes': True, 'use_enum_values': True, 'extra': 'forbid'}


class PasswordValidator(Base):
    """Password validator for Pydantic."""

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        """Enforce password security policies (length, complexity, no spaces)."""
        if len(value) < 12:
            raise ValueError('Password must be at least 12 characters')
        if ' ' in value:
            raise ValueError('Password cannot contain spaces')

        validations = (
            (PASSWORD_DIGIT_PATTERN, 'at least one digit'),
            (PASSWORD_UPPERCASE_PATTERN, 'at least one uppercase letter'),
            (PASSWORD_LOWERCASE_PATTERN, 'at least one lowercase letter'),
            (PASSWORD_SPECIAL_PATTERN, 'at least one special character'),
        )

        for pattern, requirement in validations:
            if not pattern.search(value):
                raise ValueError(f'Password must contain {requirement}')

        return value


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
