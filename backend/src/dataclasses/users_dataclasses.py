from dataclasses import dataclass

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
