"""Authentication utilities: password hashing, token generation, and session management."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, UserSession

security = HTTPBearer()

TOKEN_EXPIRY_HOURS = 24 * 7  # 7 days


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt_hex, key_hex = hashed.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return new_key == key
    except (ValueError, AttributeError):
        return False


def generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(64)


def create_session(
    db: Session,
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserSession:
    """Create a new user session with a token."""
    token = generate_token()
    session = UserSession(
        user_id=user_id,
        token=token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: extract and validate the current user from the bearer token."""
    token = credentials.credentials
    session = (
        db.query(UserSession)
        .filter(
            UserSession.token == token,
            UserSession.is_active.is_(True),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    now = datetime.now(timezone.utc)
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if expires < now:
        session.is_active = False
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    session.last_activity = now
    db.commit()

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user
