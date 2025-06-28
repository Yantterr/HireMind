from src.models import base_model


class base_user_model(base_model):
    """Base user model."""

    username: str


class user_model(base_user_model):
    """User model contains: id, username."""

    id: int


class user_create_model(base_user_model):
    """User model contains: password, username."""

    password: str


class user_login_model(user_create_model):
    """User model contains: password, username."""

    pass


class users_model(base_model):
    """Array of user_mode."""

    users: list[user_model]


class create_user_result(base_model):
    """User result."""

    token: str
    user: user_model


class token_model(base_model):
    """Model with user_agent field."""

    user_agent: str


class tokens_model(base_model):
    """Model with list of user agents."""

    id: list[token_model]
