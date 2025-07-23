from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from secrets import choice
from string import digits
from typing import Optional

from bcrypt import gensalt, hashpw
from fastapi import Request
from jwt import ExpiredSignatureError, decode, encode

from src.config import settings
from src.dataclasses.auth_dataclasses import AuthInfoDataclass, UserDataclass
from src.engines.redis_engine import AsyncRedis


def token_generate(user: UserDataclass) -> str:
    """Generate a JWT token with user dataclass and expiration."""
    expire = datetime.now(tz=timezone.utc) + timedelta(seconds=5)
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


def token_expire_verify(token: str) -> tuple[UserDataclass, bool]:
    """Verify JWT token expiration."""
    token_bytes = token.encode('utf-8')

    try:
        payload = decode(token_bytes, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
        user_dataclass = UserDataclass.from_dict(payload)

        return user_dataclass, True
    except ExpiredSignatureError:
        payload = decode(
            token_bytes,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={'verify_exp': False},
        )

        user_dataclass = UserDataclass.from_dict(payload)

        return user_dataclass, False


async def token_access_verify(token: str, user_id: int, user_agent: str, redis: AsyncRedis) -> bool:
    """Verify JWT token access."""
    redis_token = await redis.get(f'{user_id}/agent:{user_agent}')

    if redis_token == token:
        return True
    else:
        return False


async def token_save(
    old_token: str, new_token: str, user_agent: str, user_id: int, redis: AsyncRedis
) -> tuple[str, Optional[str]]:
    """Save and verify JWT token in Redis."""
    redis_token = await redis.get(f'{user_id}/agent:{user_agent}')

    if redis_token != old_token:
        all_tokens = await redis.keys(f'{user_id}/agent:*')
        await redis.delete(*all_tokens)
        return '', 'access_denied'

    await redis.set(name=f'{user_id}/agent:{user_agent}', value=new_token, expire=2_592_000)

    return new_token, None


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


def email_key_generate() -> int:
    """Generate a random key for email confirmation."""
    key = ''.join(choice(digits) for _ in range(6))

    return int(key)


def get_validated_auth_info(request: Request) -> AuthInfoDataclass:
    """Get token and user agent from request and validate them."""
    cookie_token = request.cookies.get('token')
    user_agent = request.headers.get('User-Agent')
    state_token = None

    if hasattr(request.state, 'token'):
        state_token = request.state.token
        if not isinstance(state_token, str):
            return AuthInfoDataclass(token='', user_agent='', error='undefined_error')

    if not user_agent or (not cookie_token and not state_token):
        return AuthInfoDataclass(token='', user_agent='', error='user_not_authenticated')

    if cookie_token:
        token = cookie_token
    elif state_token:
        token = state_token

    return AuthInfoDataclass(token=token, user_agent=user_agent, error=None)
