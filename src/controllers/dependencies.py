"""FastAPI dependencies shared by controllers (settings, logging)."""

from __future__ import annotations

from logging import Logger
from typing import Annotated

from fastapi import Depends

from src.core.config import Settings, settings
from src.core.logger import get_logger


def get_settings() -> Settings:
    return settings


def get_app_logger() -> Logger:
    return get_logger("ai_service.controllers")


SettingsDep = Annotated[Settings, Depends(get_settings)]
LoggerDep = Annotated[Logger, Depends(get_app_logger)]
