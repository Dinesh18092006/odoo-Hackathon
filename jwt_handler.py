"""
JWT token creation and validation.
Uses python-jose with HS256 algorithm.
Access tokens: short-lived (60 min default)
Refresh tokens: long-lived (7 days default)
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from config import settings
from utils.exceptions import UnauthorizedException


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Internal helper to create a signed JWT token."""
    payload = data.copy()
    payload["iat"] = datetime.now(timezone.utc)
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, email: str, role: str, department_id: str | None = None) -> str:
    """Create a short-lived JWT access token."""
    return _create_token(
        data={
            "sub": user_id,
            "email": email,
            "role": role,
            "department_id": department_id,
            "type": "access",
        },
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token."""
    return _create_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises UnauthorizedException if invalid, expired, or wrong type.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")


def decode_refresh_token(token: str) -> str:
    """
    Decode and validate a JWT refresh token.
    Returns the user_id (sub) claim.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")
        return user_id
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")
