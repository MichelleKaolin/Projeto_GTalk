"""Dashboard routes: analytics, usage statistics, and transcription insights."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Transcription, TTSRequest, User
from ..schemas import (
    CategoryBreakdown,
    DailyActivity,
    DashboardOverview,
    DashboardStats,
    LanguageBreakdown,
    RecentTranscription,
    SpeedDistribution,
    StatusBreakdown,
    TTSAnalytics,
    VoiceUsage,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a comprehensive dashboard overview with stats, charts, and recent activity."""
    user_id = current_user.id

    # ── Core stats ────────────────────────────────────────────────────────
    total_transcriptions = (
        db.query(func.count(Transcription.id))
        .filter(Transcription.user_id == user_id)
        .scalar()
    )
    total_duration = (
        db.query(func.coalesce(func.sum(Transcription.duration_seconds), 0.0))
        .filter(Transcription.user_id == user_id)
        .scalar()
    )
    total_words = (
        db.query(func.coalesce(func.sum(Transcription.word_count), 0))
        .filter(Transcription.user_id == user_id)
        .scalar()
    )
    completed_transcriptions = (
        db.query(func.count(Transcription.id))
        .filter(Transcription.user_id == user_id, Transcription.status == "completed")
        .scalar()
    )
    failed_transcriptions = (
        db.query(func.count(Transcription.id))
        .filter(Transcription.user_id == user_id, Transcription.status == "failed")
        .scalar()
    )
    total_tts = (
        db.query(func.count(TTSRequest.id))
        .filter(TTSRequest.user_id == user_id)
        .scalar()
    )
    total_chars = (
        db.query(func.coalesce(func.sum(TTSRequest.char_count), 0))
        .filter(TTSRequest.user_id == user_id)
        .scalar()
    )
    completed_tts = (
        db.query(func.count(TTSRequest.id))
        .filter(TTSRequest.user_id == user_id, TTSRequest.status == "completed")
        .scalar()
    )

    stats = DashboardStats(
        total_transcriptions=total_transcriptions,
        total_hours_recorded=round(float(total_duration) / 3600, 2),
        total_tts_requests=total_tts,
        total_texts_read=completed_tts,
        total_words_transcribed=total_words,
        total_chars_vocalized=total_chars,
        completed_transcriptions=completed_transcriptions,
        failed_transcriptions=failed_transcriptions,
    )

    # ── Daily activity (last N days) ──────────────────────────────────────
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    transcriptions_in_range = (
        db.query(Transcription)
        .filter(Transcription.user_id == user_id, Transcription.created_at >= cutoff)
        .all()
    )
    tts_in_range = (
        db.query(TTSRequest)
        .filter(TTSRequest.user_id == user_id, TTSRequest.created_at >= cutoff)
        .all()
    )

    daily_map: dict[str, dict[str, int]] = defaultdict(lambda: {"transcriptions": 0, "tts_requests": 0})
    for t in transcriptions_in_range:
        day_str = t.created_at.strftime("%Y-%m-%d")
        daily_map[day_str]["transcriptions"] += 1
    for t in tts_in_range:
        day_str = t.created_at.strftime("%Y-%m-%d")
        daily_map[day_str]["tts_requests"] += 1

    daily_activity = sorted(
        [
            DailyActivity(date=d, transcriptions=v["transcriptions"], tts_requests=v["tts_requests"])
            for d, v in daily_map.items()
        ],
        key=lambda x: x.date,
    )

    # ── Category breakdown ────────────────────────────────────────────────
    categories_raw = (
        db.query(
            func.coalesce(Transcription.category, "Uncategorized").label("cat"),
            func.count(Transcription.id),
            func.coalesce(func.sum(Transcription.duration_seconds), 0.0),
        )
        .filter(Transcription.user_id == user_id)
        .group_by("cat")
        .all()
    )
    category_breakdown = [
        CategoryBreakdown(
            category=row[0],
            count=row[1],
            total_duration_hours=round(float(row[2]) / 3600, 2),
        )
        for row in categories_raw
    ]

    # ── Language breakdown ────────────────────────────────────────────────
    languages_raw = (
        db.query(Transcription.language, func.count(Transcription.id))
        .filter(Transcription.user_id == user_id)
        .group_by(Transcription.language)
        .all()
    )
    language_breakdown = [
        LanguageBreakdown(language=row[0], count=row[1]) for row in languages_raw
    ]

    # ── Transcription status breakdown ────────────────────────────────────
    status_raw = (
        db.query(Transcription.status, func.count(Transcription.id))
        .filter(Transcription.user_id == user_id)
        .group_by(Transcription.status)
        .all()
    )
    transcription_status = [
        StatusBreakdown(status=row[0], count=row[1]) for row in status_raw
    ]

    # ── Recent transcriptions ─────────────────────────────────────────────
    recent = (
        db.query(Transcription)
        .filter(Transcription.user_id == user_id)
        .order_by(Transcription.created_at.desc())
        .limit(10)
        .all()
    )
    recent_transcriptions = [RecentTranscription.model_validate(t) for t in recent]

    return DashboardOverview(
        stats=stats,
        daily_activity=daily_activity,
        category_breakdown=category_breakdown,
        language_breakdown=language_breakdown,
        transcription_status=transcription_status,
        recent_transcriptions=recent_transcriptions,
    )


@router.get("/tts-analytics", response_model=TTSAnalytics)
def get_tts_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed TTS/GeniVoice analytics."""
    user_id = current_user.id
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    total_requests = (
        db.query(func.count(TTSRequest.id))
        .filter(TTSRequest.user_id == user_id)
        .scalar()
    )
    total_chars = (
        db.query(func.coalesce(func.sum(TTSRequest.char_count), 0))
        .filter(TTSRequest.user_id == user_id)
        .scalar()
    )

    # Voice usage
    voice_raw = (
        db.query(
            TTSRequest.voice,
            func.count(TTSRequest.id),
            func.coalesce(func.sum(TTSRequest.char_count), 0),
        )
        .filter(TTSRequest.user_id == user_id)
        .group_by(TTSRequest.voice)
        .all()
    )
    voice_usage = [
        VoiceUsage(voice=row[0], count=row[1], total_chars=row[2]) for row in voice_raw
    ]

    # Speed distribution
    tts_all = (
        db.query(TTSRequest.speed)
        .filter(TTSRequest.user_id == user_id)
        .all()
    )
    speed_buckets: dict[str, int] = defaultdict(int)
    for (speed,) in tts_all:
        if speed < 0.75:
            speed_buckets["0.5x - 0.75x"] += 1
        elif speed < 1.25:
            speed_buckets["0.75x - 1.25x"] += 1
        elif speed < 1.75:
            speed_buckets["1.25x - 1.75x"] += 1
        else:
            speed_buckets["1.75x - 2.0x"] += 1

    speed_distribution = [
        SpeedDistribution(speed_range=k, count=v) for k, v in sorted(speed_buckets.items())
    ]

    # Daily TTS usage
    tts_in_range = (
        db.query(TTSRequest)
        .filter(TTSRequest.user_id == user_id, TTSRequest.created_at >= cutoff)
        .all()
    )
    daily_tts_map: dict[str, int] = defaultdict(int)
    for t in tts_in_range:
        day_str = t.created_at.strftime("%Y-%m-%d")
        daily_tts_map[day_str] += 1

    daily_usage = sorted(
        [
            DailyActivity(date=d, transcriptions=0, tts_requests=c)
            for d, c in daily_tts_map.items()
        ],
        key=lambda x: x.date,
    )

    return TTSAnalytics(
        total_requests=total_requests,
        total_chars=total_chars,
        voice_usage=voice_usage,
        speed_distribution=speed_distribution,
        daily_usage=daily_usage,
    )


@router.get("/categories")
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all unique transcription categories for the current user."""
    cats = (
        db.query(Transcription.category)
        .filter(
            Transcription.user_id == current_user.id,
            Transcription.category.isnot(None),
        )
        .distinct()
        .all()
    )
    return {"categories": [c[0] for c in cats]}
