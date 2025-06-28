from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import RoleEnum


class UserSchema(Base):
    """Sqlalchemy schema of user."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    chats: Mapped[list['ChatSchema']] = relationship('ChatSchema', back_populates='user', cascade='all, delete-orphan')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChatSchema(Base):
    """Sqlalchemy schema of user."""

    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['UserSchema'] = relationship('UserSchema', back_populates='chats')

    messages: Mapped[list['MessageSchema']] = relationship('MessageSchema', back_populates='chat', cascade='all')

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    is_archived: Mapped[bool] = mapped_column(default=False)


class MessageSchema(Base):
    """Sqlalchemy schema of message."""

    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'), nullable=False)
    chat: Mapped['ChatSchema'] = relationship('ChatSchema', back_populates='messages')
    role: Mapped[str] = mapped_column(SQLEnum(RoleEnum), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
