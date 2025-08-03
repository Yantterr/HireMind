from dataclasses import dataclass

from src.dto.generally_dto import BaseDataclass
from src.models.generally_models import SystemRoleEnum


@dataclass
class UserDataclass(BaseDataclass):
    """User dataclass."""

    id: int
    username: str
    email: str
    role: SystemRoleEnum
    is_activated: bool
