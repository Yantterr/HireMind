from fastapi import Request

from src.config import settings
from src.dataclasses.users_dataclasses import UserDataclass
from src.logger import Logger


def require_permission(required_permission: str):
    """Dependency for checking user permissions."""

    async def permission_checker(request: Request) -> UserDataclass:
        user = request.state.user

        user_role_index = settings.system_roles.index(user.role)
        required_role_index = settings.system_roles.index(required_permission)

        if user_role_index < required_role_index:
            raise Logger.create_response_error(error_key='access_denied', is_cookie_remove=False)

        return user

    return permission_checker
