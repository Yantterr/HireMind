from typing import Optional

from src.models import Base, SystemRoleEnum


class BaseUserModel(Base):
    """Base user model."""

    username: Optional[str]


class UserModel(BaseUserModel):
    """User model contains: id, username."""

    role: SystemRoleEnum
    id: int


class UserCreateModel(BaseUserModel):
    """User model contains: password, username."""

    role: SystemRoleEnum
    password: Optional[str]


class UserLoginModel(Base):
    """User model contains: password, username."""

    username: str
    password: str


class UserCreateResultModel(Base):
    """User result."""

    token: str
    user: UserModel


class TokenModel(Base):
    """Model with user_agent field."""

    user_agent: str
