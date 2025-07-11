from fastapi_mail import FastMail, MessageSchema, MessageType

from src.config import settings


async def send_email_message(email_to: str, body: str, type: MessageType):
    """Send email message."""
    message = MessageSchema(subject='REGISTER.', recipients=[email_to], body=body, subtype=type)

    fm = FastMail(settings.email_config)
    return await fm.send_message(message)


# async def save_token(user_id: int, user_agent: str, redis: AsyncRedis) -> str:
# """Generate and save JWT token in Redis."""
# token = users_utils.get_token(user_id=user_id)

# user_id_str = str(user_id)

# await redis.set(name=f'{user_id_str}/agent:{user_agent}', value=token, expire=2_592_000)

# return token
