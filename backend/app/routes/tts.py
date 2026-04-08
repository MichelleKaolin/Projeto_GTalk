"""Text-to-Speech (GeniVoice) routes."""

import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import TTSRequest, User
from ..schemas import TTSRequestCreate, TTSRequestResponse

router = APIRouter(prefix="/tts", tags=["Text-to-Speech (GeniVoice)"])

AVAILABLE_VOICES = [
    {"id": "female_pt_br", "name": "Voz Feminina (Pt-BR)", "language": "pt-BR"},
    {"id": "male_pt_br", "name": "Voz Masculina (Pt-BR)", "language": "pt-BR"},
    {"id": "child_pt_br", "name": "Voz Infantil", "language": "pt-BR"},
    {"id": "female_en_us", "name": "Female Voice (EN-US)", "language": "en-US"},
    {"id": "male_en_us", "name": "Male Voice (EN-US)", "language": "en-US"},
]


@router.get("/voices")
def list_voices():
    """List all available TTS voices."""
    return {"voices": AVAILABLE_VOICES}


@router.post("/", response_model=TTSRequestResponse, status_code=status.HTTP_201_CREATED)
def create_tts_request(
    payload: TTSRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new text-to-speech request (simulates GeniVoice processing)."""
    valid_voice_ids = [v["id"] for v in AVAILABLE_VOICES]
    if payload.voice not in valid_voice_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid voice. Choose from: {valid_voice_ids}",
        )

    tts = TTSRequest(
        user_id=current_user.id,
        input_text=payload.input_text,
        voice=payload.voice,
        speed=payload.speed,
        char_count=len(payload.input_text),
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )
    db.add(tts)
    db.commit()
    db.refresh(tts)
    return TTSRequestResponse.model_validate(tts)


@router.get("/", response_model=dict)
def list_tts_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    voice: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all TTS requests for the current user."""
    query = db.query(TTSRequest).filter(TTSRequest.user_id == current_user.id)

    if voice:
        query = query.filter(TTSRequest.voice == voice)

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))
    items = (
        query.order_by(TTSRequest.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [TTSRequestResponse.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{tts_id}", response_model=TTSRequestResponse)
def get_tts_request(
    tts_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single TTS request by ID."""
    tts = (
        db.query(TTSRequest)
        .filter(TTSRequest.id == tts_id, TTSRequest.user_id == current_user.id)
        .first()
    )
    if not tts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TTS request not found")
    return TTSRequestResponse.model_validate(tts)


@router.delete("/{tts_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tts_request(
    tts_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a TTS request."""
    tts = (
        db.query(TTSRequest)
        .filter(TTSRequest.id == tts_id, TTSRequest.user_id == current_user.id)
        .first()
    )
    if not tts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TTS request not found")
    db.delete(tts)
    db.commit()
