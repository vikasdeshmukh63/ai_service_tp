"""Minimal `users` row shape for auth checks (matches auth_service Sequelize `User` table)."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
