from fastapi_mail import FastMail, MessageSchema, MessageType

from src.config import settings


async def send_email_message(email_to: str, body: str, type: MessageType):
    """Send email message."""
    message = MessageSchema(subject='REGISTER.', recipients=[email_to], body=body, subtype=type)

    fm = FastMail(settings.email_config)
    return await fm.send_message(message)
