"""
Bearer PASETO auth — mirrors auth_service `requireAuth` (token + user exists + email verified).
Used by controllers as FastAPI dependencies.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.core.auth import verify_access_token
from src.core.config import settings
from src.core.database import get_db
from src.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _parse_user_id(raw: object) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw if raw > 0 else None
    if isinstance(raw, str):
        try:
            n = int(raw, 10)
        except ValueError:
            return None
        return n if n > 0 else None
    return None


def get_bearer_payload(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    if not (settings.paseto_public_key or "").strip():
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured (set PASETO_PUBLIC_KEY).",
        )
    try:
        return verify_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None


def get_current_user(
    payload: Annotated[dict, Depends(get_bearer_payload)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    raw = payload.get("sub")
    user_id = _parse_user_id(raw)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        user = db.get(User, user_id)
    except OperationalError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database unavailable. Set DATABASE_URL to the same Neon connection string as "
                "auth_service (copy from auth_service/.env). Do not use placeholder hostnames "
                "from .env.example."
            ),
        ) from e

    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")

    if not user.email_verified:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Please verify your email before using this resource.",
                "code": "EMAIL_NOT_VERIFIED",
            },
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
