from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models.generally_models import NNRoleEnum, SystemRoleEnum


class SqlalchemyBase(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class UserSchema(SqlalchemyBase):
    """ORM model representing a user."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    role: Mapped[SystemRoleEnum] = mapped_column(
        SQLEnum(SystemRoleEnum),
        nullable=False,
        default=SystemRoleEnum.USER.value,
        server_default=SystemRoleEnum.USER.value,
    )

    username: Mapped[Optional[str]] = mapped_column(unique=True, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(256), unique=True, nullable=True)
    chats: Mapped[list['ChatSchema']] = relationship('ChatSchema', back_populates='user', cascade='all, delete-orphan')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_activated: Mapped[bool] = mapped_column(default=False, server_default=text('true'), nullable=False)


class ChatSchema(SqlalchemyBase):
    """ORM model representing a chat session."""

    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['UserSchema'] = relationship('UserSchema', back_populates='chats')

    messages: Mapped[list['MessageSchema']] = relationship('MessageSchema', back_populates='chat', cascade='all')

    count_request_tokens: Mapped[int] = mapped_column(default=0)
    count_response_tokens: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    is_archived: Mapped[bool] = mapped_column(default=False)


class MessageSchema(SqlalchemyBase):
    """ORM model representing a message within a chat."""

    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    chat: Mapped['ChatSchema'] = relationship('ChatSchema', back_populates='messages')
    role: Mapped[str] = mapped_column(SQLEnum(NNRoleEnum), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
