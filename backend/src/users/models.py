from src.models import Base


class BaseUserModel(Base):
    """Base user model."""

    username: str


class UserModel(BaseUserModel):
    """User model contains: id, username."""

    id: int


class UserCreateModel(BaseUserModel):
    """User model contains: password, username."""

    password: str


class UserLoginModel(UserCreateModel):
    """User model contains: password, username."""

    pass


class UserCreateResultModel(Base):
    """User result."""

    token: str
    user: UserModel


class TokenModel(Base):
    """Model with user_agent field."""

    user_agent: str
