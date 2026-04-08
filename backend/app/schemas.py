"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Session Schemas ───────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    id: str
    user_id: str
    is_active: bool
    ip_address: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

    model_config = {"from_attributes": True}


# ── Transcription Schemas ─────────────────────────────────────────────────────

class TranscriptionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    language: str = Field(default="pt-BR", max_length=10)
    category: Optional[str] = Field(default=None, max_length=100)


class TranscriptionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=300)
    transcribed_text: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, pattern="^(pending|processing|completed|failed)$")


class TranscriptionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_filename: Optional[str] = None
    transcribed_text: Optional[str] = None
    language: str
    duration_seconds: Optional[float] = None
    word_count: int
    status: str
    category: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TranscriptionSimulate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    text: str = Field(..., min_length=1)
    duration_seconds: Optional[float] = Field(default=None, ge=0)
    language: str = Field(default="pt-BR", max_length=10)
    category: Optional[str] = Field(default=None, max_length=100)


# ── TTS Schemas ───────────────────────────────────────────────────────────────

class TTSRequestCreate(BaseModel):
    input_text: str = Field(..., min_length=1)
    voice: str = Field(default="female_pt_br", max_length=50)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class TTSRequestResponse(BaseModel):
    id: str
    user_id: str
    input_text: str
    voice: str
    speed: float
    char_count: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Dashboard Schemas ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_transcriptions: int
    total_hours_recorded: float
    total_tts_requests: int
    total_texts_read: int
    total_words_transcribed: int
    total_chars_vocalized: int
    completed_transcriptions: int
    failed_transcriptions: int


class DailyActivity(BaseModel):
    date: str
    transcriptions: int
    tts_requests: int


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    total_duration_hours: float


class LanguageBreakdown(BaseModel):
    language: str
    count: int


class StatusBreakdown(BaseModel):
    status: str
    count: int


class RecentTranscription(BaseModel):
    id: str
    title: str
    status: str
    word_count: int
    duration_seconds: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardOverview(BaseModel):
    stats: DashboardStats
    daily_activity: list[DailyActivity]
    category_breakdown: list[CategoryBreakdown]
    language_breakdown: list[LanguageBreakdown]
    transcription_status: list[StatusBreakdown]
    recent_transcriptions: list[RecentTranscription]


class VoiceUsage(BaseModel):
    voice: str
    count: int
    total_chars: int


class SpeedDistribution(BaseModel):
    speed_range: str
    count: int


class TTSAnalytics(BaseModel):
    total_requests: int
    total_chars: int
    voice_usage: list[VoiceUsage]
    speed_distribution: list[SpeedDistribution]
    daily_usage: list[DailyActivity]


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
