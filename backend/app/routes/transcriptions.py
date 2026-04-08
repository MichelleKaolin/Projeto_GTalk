"""Transcription routes: CRUD operations and audio upload simulation."""

import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Transcription, User
from ..schemas import (
    TranscriptionCreate,
    TranscriptionResponse,
    TranscriptionSimulate,
    TranscriptionUpdate,
)

router = APIRouter(prefix="/transcriptions", tags=["Transcriptions"])


@router.get("/", response_model=dict)
def list_transcriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all transcriptions for the current user with pagination and filters."""
    query = db.query(Transcription).filter(Transcription.user_id == current_user.id)

    if status_filter:
        query = query.filter(Transcription.status == status_filter)
    if category:
        query = query.filter(Transcription.category == category)
    if search:
        query = query.filter(
            (Transcription.title.ilike(f"%{search}%"))
            | (Transcription.transcribed_text.ilike(f"%{search}%"))
        )

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))
    items = (
        query.order_by(Transcription.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [TranscriptionResponse.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_transcription(
    payload: TranscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new transcription record (pending audio upload)."""
    transcription = Transcription(
        user_id=current_user.id,
        title=payload.title,
        language=payload.language,
        category=payload.category,
        status="pending",
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    return TranscriptionResponse.model_validate(transcription)


@router.post("/simulate", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
def simulate_transcription(
    payload: TranscriptionSimulate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simulate a completed transcription (for demo/testing without real audio)."""
    word_count = len(payload.text.split())
    duration = payload.duration_seconds if payload.duration_seconds else word_count * 0.5

    transcription = Transcription(
        user_id=current_user.id,
        title=payload.title,
        transcribed_text=payload.text,
        language=payload.language,
        category=payload.category,
        duration_seconds=duration,
        word_count=word_count,
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)
    return TranscriptionResponse.model_validate(transcription)


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(
    transcription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single transcription by ID."""
    transcription = (
        db.query(Transcription)
        .filter(
            Transcription.id == transcription_id,
            Transcription.user_id == current_user.id,
        )
        .first()
    )
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
    return TranscriptionResponse.model_validate(transcription)


@router.patch("/{transcription_id}", response_model=TranscriptionResponse)
def update_transcription(
    transcription_id: str,
    payload: TranscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a transcription's metadata or text."""
    transcription = (
        db.query(Transcription)
        .filter(
            Transcription.id == transcription_id,
            Transcription.user_id == current_user.id,
        )
        .first()
    )
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transcription, field, value)

    if payload.transcribed_text is not None:
        transcription.word_count = len(payload.transcribed_text.split())

    if payload.status == "completed" and transcription.completed_at is None:
        transcription.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(transcription)
    return TranscriptionResponse.model_validate(transcription)


@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcription(
    transcription_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transcription."""
    transcription = (
        db.query(Transcription)
        .filter(
            Transcription.id == transcription_id,
            Transcription.user_id == current_user.id,
        )
        .first()
    )
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")
    db.delete(transcription)
    db.commit()
