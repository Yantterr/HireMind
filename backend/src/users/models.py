from typing import Optional

from src.models import Base, SystemRoleEnum


class BaseUserModel(Base):
    """Base user model with optional username."""

    username: Optional[str]


class UserModel(BaseUserModel):
    """User model with ID and role."""

    id: int
    role: SystemRoleEnum


class UserCreateModel(BaseUserModel):
    """User creation model with optional password and role."""

    password: Optional[str]
    role: SystemRoleEnum


class UserLoginModel(Base):
    """User login model with required username and password."""

    username: str
    password: str


class UserCreateResultModel(Base):
    """Result model for user creation containing token and user info."""

    token: str
    user: UserModel


class TokenModel(Base):
    """Model containing user agent string."""

    user_agent: str
