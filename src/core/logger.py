"""
Structured logging aligned with auth_service `logger.ts` (Winston):
- Console: colorized, short timestamp
- File: ISO-like timestamp, level, message, optional JSON metadata
- `LOG_LEVEL` / production default like Node; `LOG_FILE` default `logs/log.txt`
"""

from __future__ import annotations

import json
import logging
import sys
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import colorlog

from src.core.config import settings

_configured_loggers: set[str] = set()


def _ensure_log_dir(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def _build_file_handler() -> RotatingFileHandler:
    path = (
        Path(settings.log_file)
        if Path(settings.log_file).is_absolute()
        else Path.cwd() / settings.log_file
    )
    _ensure_log_dir(path)
    handler = RotatingFileHandler(path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setLevel(settings.resolved_log_level.upper())

    class FileFmt(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            ts = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
            level = record.levelname.lower()
            base = record.getMessage()
            if record.exc_info:
                base = f"{base}\n{self.formatException(record.exc_info)}"
            extra = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in (
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "message",
                )
                and not k.startswith("_")
            }
            meta = f" {json.dumps(extra)}" if extra else ""
            return f"{ts} [{level}] {base}{meta}"

    handler.setFormatter(FileFmt())
    return handler


def _build_console_handler() -> logging.Handler:
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setLevel(settings.resolved_log_level.upper())
    fmt = "%(log_color)s%(asctime)s %(levelname)s%(reset)s %(message)s"
    datefmt = "%H:%M:%S"
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt,
            datefmt=datefmt,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    return handler


def get_logger(name: str = "ai_service") -> Logger:
    """Return a module-level logger with file + console sinks (idempotent)."""
    log = logging.getLogger(name)
    if name in _configured_loggers:
        return log
    log.setLevel(settings.resolved_log_level.upper())
    log.handlers.clear()
    log.addHandler(_build_console_handler())
    log.addHandler(_build_file_handler())
    log.propagate = False
    _configured_loggers.add(name)
    return log


def log_extra(**kwargs: Any) -> dict[str, Any]:
    """Attach structured fields (mirrors Winston `meta` / JSON rest object)."""
    return kwargs
