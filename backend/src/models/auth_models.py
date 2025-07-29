from re import compile
from typing import Optional

from pydantic import field_validator

from src.models.generally_models import Base, SystemRoleEnum

PASSWORD_DIGIT_PATTERN = compile(r'\d')
PASSWORD_UPPERCASE_PATTERN = compile(r'[A-Z]')
PASSWORD_LOWERCASE_PATTERN = compile(r'[a-z]')
PASSWORD_SPECIAL_PATTERN = compile(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]')


class BaseUserModel(Base):
    """Base model for user entities with optional username field."""

    username: Optional[str] = None


class UserModel(BaseUserModel):
    """Extended user model with ID, authentication status, and system role."""

    id: int
    email: Optional[str] = None
    role: SystemRoleEnum
    is_activated: bool


class UserLoginModel(Base):
    """Authentication model with email and password validation."""

    email: str
    password: str

    @field_validator('password')
    def validate_password(cls, value: str) -> str:
        """Enforce password security policies (length, complexity, no spaces)."""
        if len(value) < 12:
            raise ValueError('Password must be at least 12 characters')
        if ' ' in value:
            raise ValueError('Password cannot contain spaces')

        # Validate required character types
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


class UserCreateModel(UserLoginModel):
    """User registration model extending authentication with required username."""

    username: str


class UserConfirmEmailModel(Base):
    """Email verification model containing confirmation key."""

    key: int
