from dataclasses import dataclass

from src.dataclasses.generally import BaseDataclass
from src.models.generally import SystemRoleEnum


@dataclass
class UserDataclass(BaseDataclass):
    """User dataclass."""

    id: int
    username: str
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
