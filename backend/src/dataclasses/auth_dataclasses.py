from dataclasses import dataclass
from typing import Optional

from src.dataclasses.generally_dataclasses import BaseDataclass
from src.models.generally_models import SystemRoleEnum


@dataclass
class UserDataclass(BaseDataclass):
    """User dataclass."""

    id: int
    username: str
    email: str
    role: SystemRoleEnum
    is_activated: bool


@dataclass
class UserCreateDataclass:
    """User create dataclass."""

    user: UserDataclass
    token: str
    key: int


@dataclass
class UserLoginDataclass:
    """Login dataclass."""

    token: str
    user: UserDataclass


@dataclass
class AuthDataclass:
    """Auth dataclass."""

    user: UserDataclass
    user_agent: str
    token: str


@dataclass
class AuthInfoDataclass:
    """Auth info dataclass."""

    token: str
    user_agent: str
    error: Optional[str]
