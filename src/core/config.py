"""
Centralized settings from the environment.
Mirrors auth_service `loadEnv.ts` + `env.ts`: loads `.env`, then `.env.<APP_ENV>` when present.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_ENVS = ("dev", "qa", "uat", "production")
AppEnv = Literal["dev", "qa", "uat", "production"]


def _resolve_app_env(raw: str | None) -> AppEnv:
    key = (raw or "").strip().lower() or "dev"
    if key not in APP_ENVS:
        raise ValueError(f'Invalid APP_ENV="{raw}". Must be one of: {", ".join(APP_ENVS)}')
    return key  # type: ignore[return-value]


def load_env_files(cwd: Path | None = None) -> dict[str, object]:
    """Load `.env`, then `.env.<APP_ENV>` with override (same order as Node `loadEnv.ts`)."""
    root = cwd or Path.cwd()
    load_dotenv(root / ".env")
    raw = os.environ.get("APP_ENV")
    app_env = _resolve_app_env(raw)
    os.environ["APP_ENV"] = app_env
    overlay = root / f".env.{app_env}"
    overlay_loaded = overlay.is_file()
    if overlay_loaded:
        load_dotenv(overlay, override=True)
    return {
        "app_env": app_env,
        "overlay_file_name": f".env.{app_env}",
        "overlay_path": str(overlay.resolve()),
        "overlay_loaded": overlay_loaded,
    }


# Run once at import so settings and logging see the same env as the auth service
env_load_info: dict[str, object] = load_env_files()


class Settings(BaseSettings):
    """Application configuration (secrets and URLs from the environment)."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: AppEnv = Field(default="dev", validation_alias="APP_ENV")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    port: int = Field(default=8000, validation_alias="PORT")

    log_level: str | None = Field(default=None, validation_alias="LOG_LEVEL")
    log_file: str = Field(default="logs/log.txt", validation_alias="LOG_FILE")

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    # PASETO v4.public — same `PASETO_PUBLIC_KEY` as auth_service (Paserk). Verify-only.
    paseto_public_key: str | None = Field(default=None, validation_alias="PASETO_PUBLIC_KEY")

    # PostgreSQL (e.g. Neon) — same `DATABASE_URL` pattern as auth_service
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")

    # Comma-separated browser origins allowed to call this API (Next.js dev, prod URL, etc.)
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        validation_alias="CORS_ORIGINS",
    )

    @model_validator(mode="before")
    @classmethod
    def sync_app_env(cls, data: object) -> object:
        if isinstance(data, dict) and "APP_ENV" in data:
            data["APP_ENV"] = _resolve_app_env(str(data.get("APP_ENV")))
        return data

    @computed_field  # type: ignore[prop-decorator]
    @property
    def resolved_log_level(self) -> str:
        if self.log_level:
            return self.log_level
        return "info" if self.environment == "production" else "debug"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
