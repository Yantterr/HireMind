from datetime import datetime, timedelta, timezone

import jwt
from bcrypt import gensalt, hashpw

from src.config import settings
from src.logger import Logger


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = gensalt(10)

    hashed_password = hashpw(password.encode('utf-8'), salt)

    return hashed_password.decode('utf-8')


def get_token(user_id: int) -> str:
    """Generate a JWT token with user ID and expiration."""
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    encoded_jwt = jwt.encode(
        payload={'sub': str(user_id), 'exp': int(expire.timestamp())},
        key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str) -> int:
    """Decode JWT token and extract user ID, handling expiration and errors."""
    try:
        token_bytes = token.encode('utf-8')

        payload = jwt.decode(token_bytes, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get('sub')
        if user_id is None:
            raise ValueError("Token payload missing 'sub' field")

        return int(user_id)
    except jwt.ExpiredSignatureError as err:
        raise Logger.create_response_error(error_key='token_expired', is_cookie_remove=True) from err
    except jwt.PyJWTError as e:
        raise e from e
    except ValueError as e:
        raise e from e


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hashed version."""
    is_valid = hashpw(
        password=password.encode('utf-8'), salt=hashed_password.encode('utf-8')
    ) == hashed_password.encode('utf-8')

    return is_valid
