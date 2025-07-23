from fastapi import HTTPException

from src.config import settings


class Logger:
    """Logger errors."""

    errors = {
        'data_not_found': (404, 'Data not found'),
        'user_not_authenticated': (401, 'Not authenticated'),
        'user_not_found': (404, 'User not found'),
        'access_denied': (403, 'Access denied'),
        'user_already_exists': (409, 'User already exists'),
        'password_not_correct': (401, 'Password not correct'),
        'undefined_error': (500, 'Undefined error'),
        'token_expired': (401, 'Token expired'),
    }

    @staticmethod
    def create_response_error(error_key: str, is_cookie_remove: bool = False) -> HTTPException:
        """Create response error."""
        if error_key not in Logger.errors:
            raise ValueError(f'Unknown error key: {error_key}')

        status, detail = Logger.errors[error_key]

        headers = None
        if is_cookie_remove:
            samesite = 'None' if settings.develop_mode else 'Lax'
            secure = '' if settings.develop_mode else 'Secure'

            cookie = f'token=; Max-Age=0; Path=/; SameSite={samesite}'
            if secure:
                cookie += f'; {secure}'

            headers = {'set-cookie': cookie}

        return HTTPException(status_code=status, detail=detail, headers=headers)
