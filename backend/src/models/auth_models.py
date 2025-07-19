from re import search
from typing import Optional

from pydantic import field_validator

from src.models.generally_models import Base, SystemRoleEnum


class BaseUserModel(Base):
    """Base user model with optional username."""

    username: Optional[str] = None


class UserModel(BaseUserModel):
    """User model with ID and role."""

    id: int
    email: Optional[str] = None
    role: SystemRoleEnum
    is_activated: bool


class UserLoginModel(Base):
    """User login model with required username and password."""

    email: str
    password: str

    @field_validator('password')
    def validate_password(cls, value):
        """Validate password."""
        if len(value) < 12:
            raise ValueError('Password must be at least 12 characters long')

        if not search(r'\d', value):
            raise ValueError('Password must contain at least one digit')

        if not search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')

        if not search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')

        if not search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', value):
            raise ValueError('Password must contain at least one special character')

        if ' ' in value:
            raise ValueError('Password cannot contain spaces')

        if value.lower() == value:
            raise ValueError('Password must contain mixed case characters')

        if value.isalnum():
            raise ValueError('Password must contain at least one special character')

        return value


class UserCreateModel(UserLoginModel):
    """User creation model with optional password and role."""

    username: str


class UserConfirmEmailModel(Base):
    """User confirm email model."""

    key: int


# class UserCreateResultModel(Base):
#     """Result model for user creation containing token and user info."""

#     token: str
#     user: UserModel


# class TokenModel(Base):
#     """Model containing user agent string."""

#     user_agent: str
