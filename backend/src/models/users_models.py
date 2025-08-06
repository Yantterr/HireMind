from typing import Optional

from pydantic import EmailStr, Field

from src.models.auth_models import BaseUserModel
from src.models.generally_models import Base, PasswordField, SystemRoleEnum


class KeyConfirmationMixin(Base):
    """Mixin model for operations requiring confirmation key."""

    key: int = Field(..., ge=100000, le=999999, description='6-digit verification code')


class PasswordOperationsMixin(PasswordField):
    """Mixin model for password-related operations."""

    pass


class UserModel(BaseUserModel):
    """Complete user model with authentication status and system role."""

    id: int
    email: Optional[EmailStr] = Field(None, description="User's email address")
    role: SystemRoleEnum = Field(..., description="User's system role")
    is_activated: bool = Field(False, description='Account activation status')


class UserEditPasswordModel(PasswordOperationsMixin):
    """Model for changing user password."""

    password_old: str = Field(..., description='Current password')
    password: str = Field(..., description='New password')


class UserResetPasswordModel(KeyConfirmationMixin, PasswordOperationsMixin):
    """Model for password reset operation."""

    pass


class UserEditEmailModel(KeyConfirmationMixin):
    """Model for changing user email."""

    email: EmailStr = Field(..., description='New email address')


class UserEditNameModel(Base):
    """Model for changing username."""

    username: str = Field(..., min_length=3, max_length=20, description='New username')
