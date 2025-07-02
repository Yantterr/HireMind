from sqlalchemy.ext.asyncio import AsyncSession

import src.users.service as users_service
import src.users.utils as users_utils
import src.utils as generally_utils
from src.database import AsyncRedis
from src.logger import Logger
from src.schemas import UserSchema
from src.users.models import UserCreateModel, UserCreateResultModel, UserLoginModel


async def get_users(db: AsyncSession) -> list[UserSchema]:
    """Get all users."""
    users = await users_service.get_users(db)
    return users


async def get_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Get user by id."""
    user = await users_service.get_user(db, user_id)
    if not user:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)
    return user


async def refresh_token(user_agent: str, token: str, db: AsyncSession, redis: AsyncRedis) -> str:
    """Refresh jwt token."""
    user_id = (await generally_utils.authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id
    user_id_str = str(user_id)

    new_token = users_utils.get_token(user_id=user_id)

    await redis.set(name=f'{user_id_str}/agent:{user_agent}', value=new_token, expire=2_592_000)

    return new_token


async def get_current_user(token: str, db: AsyncSession, redis: AsyncRedis, user_agent: str) -> UserSchema:
    """Get and validate user token."""
    user_id = (await generally_utils.authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id

    user = await users_service.get_user(db=db, user_id=user_id)

    if not user:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=True)

    return user


async def create_user(
    db: AsyncSession,
    redis: AsyncRedis,
    user_agent: str,
    user_create_data: UserCreateModel,
) -> UserCreateResultModel:
    """Create user."""
    user = await users_service.get_user_by_username(db=db, username=user_create_data.username)

    if user is not None:
        raise Logger.create_response_error(error_key='user_already_exists', is_cookie_remove=False)

    new_user = await users_service.create_user(db=db, user=user_create_data)

    token = users_utils.get_token(user_id=new_user.id)

    await redis.set(name=f'{str(new_user.id)}/agent:{user_agent}', value=token, expire=2_592_000)

    return UserCreateResultModel(token=token, user=new_user)  # type: ignore


async def logout_user(token: str, user_agent: str, db: AsyncSession, redis: AsyncRedis) -> str:
    """Logout user."""
    user_id_str = str(
        (await generally_utils.authorize_user(token=token, db=db, user_agent=user_agent, redis=redis)).id
    )

    await redis.delete(f'{user_id_str}/agent:{user_agent}')

    return 'Successfully logged out'


async def login_user(
    db: AsyncSession,
    redis: AsyncRedis,
    user_agent: str,
    login_data: UserLoginModel,
) -> str:
    """Login user."""
    user = await users_service.get_user_by_username(db, login_data.username)

    if user is None:
        raise Logger.create_response_error(error_key='data_not_found', is_cookie_remove=False)

    password_correct = users_utils.verify_password(login_data.password, user.password)

    if not password_correct:
        raise Logger.create_response_error(error_key='password_not_correct', is_cookie_remove=False)

    user_id_str = str(user.id)

    token = users_utils.get_token(user_id=user.id)

    await redis.set(name=f'{user_id_str}/agent:{user_agent}', value=token, expire=2_592_000)

    return token
