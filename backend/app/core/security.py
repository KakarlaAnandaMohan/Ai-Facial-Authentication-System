from datetime import datetime, timedelta
from typing import Any, Dict, Optional


from jose import JWTError, jwt
from app.core.config import settings

# ----------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256)
# ----------------------------------------------------------------------
import os
import base64
import hashlib


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its PBKDF2 hash stored as base64(salt+hash)."""
    data = base64.b64decode(hashed_password.encode())
    salt = data[:16]
    stored_hash = data[16:]
    dk = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt, 100_000)
    return dk == stored_hash


def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random 16‑byte salt.

    Returns a base64‑encoded string containing salt + derived key.
    """
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return base64.b64encode(salt + dk).decode()

# ----------------------------------------------------------------------
# JWT token utilities
# ----------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, role: Optional[str] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    if role:
        to_encode["role"] = role
    elif "role" not in to_encode:
        to_encode["role"] = "user"
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_admin_token(email: str = "admin@system.local") -> str:
    return create_access_token({"sub": email, "role": "admin"})

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise Exception(f"Token decode error: {e}")

# ----------------------------------------------------------------------
# Security‑header middleware (FastAPI)
# ----------------------------------------------------------------------
def setup_security_headers(app):
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=()"
        return response

