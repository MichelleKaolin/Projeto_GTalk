"""Authentication routes: signup, login, logout, and session management."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..auth import (
    create_session,
    get_current_user,
    hash_password,
    verify_password,
)
from ..database import get_db
from ..models import User, UserSession
from ..schemas import (
    SessionResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user and return an access token."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    session = create_session(
        db,
        user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return TokenResponse(
        access_token=session.token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate a user and return an access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    session = create_session(
        db,
        user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return TokenResponse(
        access_token=session.token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Invalidate the current session token."""
    auth_header = request.headers.get("authorization", "")
    token = auth_header.replace("Bearer ", "")

    session = (
        db.query(UserSession)
        .filter(UserSession.token == token, UserSession.is_active.is_(True))
        .first()
    )
    if session:
        session.is_active = False
        db.commit()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.get("/sessions", response_model=list[SessionResponse])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active sessions for the current user."""
    sessions = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active.is_(True),
        )
        .order_by(UserSession.created_at.desc())
        .all()
    )
    return [SessionResponse.model_validate(s) for s in sessions]
