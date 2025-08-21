from src.models.generally_models import Base, PasswordField


class AuthLoginModel(PasswordField):
    """Authentication model with email and password validation."""

    email: str
    password: str


class AuthCreateModel(AuthLoginModel):
    """User registration model extending authentication with required username."""

    username: str


class UserKeyModel(Base):
    """Email verification model containing confirmation key."""

    key: int
