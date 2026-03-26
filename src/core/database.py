"""
PostgreSQL via SQLAlchemy — same `DATABASE_URL` usage as auth_service (e.g. Neon).

Use `get_db()` as a FastAPI dependency when you add repositories / models.
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base (shared with models)."""


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _normalize_database_url(url: str) -> str:
    """Use psycopg (v3) driver with standard postgresql:// URLs."""
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


def get_engine() -> Engine:
    """Lazy singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        if not settings.database_url:
            raise HTTPException(
                status_code=503,
                detail="DATABASE_URL is not set.",
            )
        _engine = create_engine(
            _normalize_database_url(settings.database_url),
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
