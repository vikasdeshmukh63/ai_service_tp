"""
LangGraph shared state for CV parsing + RAG.
Extend with `TypedDict` or `pydantic.BaseModel` as graphs grow.
"""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class RagGraphState(TypedDict):
    """Example state for chunking → embedding → vector store."""

    document_id: str
    chunks: NotRequired[list[str]]
    embeddings: NotRequired[list[list[float]]]
    metadata: NotRequired[dict[str, Any]]
