from pydantic import BaseModel


class base_model(BaseModel):
    """Base model with config pydantic for sqlalchemy."""

    model_config = {'from_attributes': True}


class message_model(base_model):
    """Model with message field."""

    message: str


class token_model(base_model):
    """Model with user_agent field."""

    user_agent: str


class tokens_model(base_model):
    """Model with list of user agents."""

    id: list[token_model]
