"""FastAPI entrypoint — AI service (JD parsing)."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.controllers.jd_controller import router as jd_router
from src.core.config import env_load_info, settings
from src.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(
        "Starting ai_service",
        extra={
            "app_env": env_load_info["app_env"],
            "overlay_loaded": env_load_info["overlay_loaded"],
            "overlay": env_load_info["overlay_file_name"],
        },
    )
    yield
    logger.info("Shutting down ai_service")


app = FastAPI(
    title="AI Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(jd_router, prefix="/api/v1", tags=["job-description"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai_service", "app_env": settings.app_env}
