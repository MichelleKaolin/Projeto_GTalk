"""SQLAlchemy models for GTalk application."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    transcriptions = relationship("Transcription", back_populates="user", cascade="all, delete-orphan")
    tts_requests = relationship("TTSRequest", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(512), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="sessions")


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    original_filename = Column(String(300), nullable=True)
    audio_file_path = Column(String(500), nullable=True)
    transcribed_text = Column(Text, nullable=True)
    language = Column(String(10), default="pt-BR")
    duration_seconds = Column(Float, nullable=True)
    word_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="transcriptions")


class TTSRequest(Base):
    __tablename__ = "tts_requests"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    voice = Column(String(50), default="female_pt_br")
    speed = Column(Float, default=1.0)
    char_count = Column(Integer, default=0)
    audio_file_path = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tts_requests")
