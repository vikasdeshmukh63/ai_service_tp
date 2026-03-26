"""MVC controller: job description PDF parsing."""

from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PyPDF2 import PdfReader

from src.controllers.auth_deps import get_current_user
from src.controllers.dependencies import LoggerDep
from src.services.ai_parser_service import extract_jd_fields
from src.views.jd_schema import JDExtractionSchema

router = APIRouter(dependencies=[Depends(get_current_user)])


def _is_pdf(content: bytes, content_type: str | None) -> bool:
    if content.startswith(b"%PDF"):
        return True
    if content_type and "pdf" in content_type.lower():
        return True
    return False


@router.post("/parse-jd", response_model=JDExtractionSchema)
async def parse_jd(
    log: LoggerDep,
    file: Annotated[UploadFile, File()],
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    if not _is_pdf(content, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type: upload a PDF (expected %PDF header or application/pdf).",
        )

    reader = PdfReader(BytesIO(content))
    text_parts: list[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    pdf_text = "\n".join(text_parts).strip()

    if not pdf_text:
        log.warning("PDF contained no extractable text", extra={"filename": file.filename})
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from PDF (empty or image-only).",
        )

    try:
        result = await asyncio.to_thread(extract_jd_fields, pdf_text)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        log.exception("JD extraction failed", extra={"filename": file.filename})
        raise HTTPException(status_code=502, detail="JD extraction failed.") from e

    return result
