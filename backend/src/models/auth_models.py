from typing import Optional

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
