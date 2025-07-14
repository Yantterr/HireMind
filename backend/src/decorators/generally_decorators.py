from functools import wraps

from src.database import session_factory


def get_session(func):
    """Decorator to manage database session."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with session_factory() as session:
            async with session.begin():
                return await func(*args, db=session, **kwargs)

    return wrapper
