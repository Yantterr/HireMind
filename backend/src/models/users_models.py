from typing import Optional

from src.models.auth_models import BaseUserModel
from src.models.generally_models import Base, PasswordValidator, SystemRoleEnum


class UserModel(BaseUserModel):
    """Extended user model with ID, authentication status, and system role."""

    id: int
    email: Optional[str] = None
    role: SystemRoleEnum
    is_activated: bool


class UserEditPasswordModel(PasswordValidator):
    """Change password model containing new password and confirmation key."""

    password_old: str
    password: str


class UserResetPasswordModel(PasswordValidator):
    """Reset password model containing new password and confirmation key."""

    key: int
    password: str


class UserEditEmailModel(Base):
    """Change email model containing new email and confirmation key."""

    email: str
    key: int


class UserEditNameModel(Base):
    """User edit name model."""

    username: str
