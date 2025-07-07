from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models import NNRoleEnum, SystemRoleEnum


class SqlalchemyBase(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class UserSchema(SqlalchemyBase):
    """ORM model representing a user."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    role: Mapped[str] = mapped_column(
        SQLEnum(SystemRoleEnum),
        nullable=False,
        default=SystemRoleEnum.USER.value,
        server_default=SystemRoleEnum.USER.value,
    )

    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(128), nullable=True)
    chats: Mapped[list['ChatSchema']] = relationship('ChatSchema', back_populates='user', cascade='all, delete-orphan')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


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

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
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
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AnonymousUserSchema(SqlalchemyBase):
    """ORM model representing an anonymous user mapping."""

    __tablename__ = 'anonymous_users'

    hash: Mapped[str] = mapped_column(primary_key=True, nullable=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
