from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from bcrypt import gensalt, hashpw
from jwt import ExpiredSignatureError, decode, encode

from src.config import settings
from src.dataclasses.auth_dataclasses import UserDataclass
from src.logger import Logger


def get_token(user: UserDataclass) -> str:
    """Generate a JWT token with user dataclass and expiration."""
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    user_dict = asdict(user)

    payload = {
        **user_dict,
        'exp': int(expire.timestamp()),
    }

    encoded_jwt = encode(
        payload=payload,
        key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> UserDataclass:
    try:
        """Decode JWT token and extract user ID, handling expiration and errors."""
        token_bytes = token.encode('utf-8')

        payload = decode(token_bytes, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
        if not payload:
            raise ValueError("Token payload missing 'sub' field")

        return UserDataclass(
            username=payload['username'], is_activated=payload['is_activated'], id=payload['id'], role=payload['role']
        )
    except ExpiredSignatureError as e:
        raise Logger.create_response_error(error_key='token_expired', is_cookie_remove=False) from e


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = gensalt(10)

    hashed_password = hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hashed version."""
    is_valid = hashpw(
        password=password.encode('utf-8'), salt=hashed_password.encode('utf-8')
    ) == hashed_password.encode('utf-8')

    return is_valid
