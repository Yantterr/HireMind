from dataclasses import dataclass
from typing import Optional

from src.dto.users_dto import UserDataclass


@dataclass
class AuthDataclass:
    """Auth dataclass."""

    user: UserDataclass
    user_agent: str
    token: str


@dataclass
class AuthRegisterDataclass:
    """User create dataclass."""

    user: UserDataclass
    token: str
    key: int


@dataclass
class AuthSessionDataclass:
    """Login dataclass."""

    token: str
    user: UserDataclass


@dataclass
class AuthInfoDataclass:
    """Auth info dataclass."""

    token: str
    user_agent: str
    error: Optional[str]
