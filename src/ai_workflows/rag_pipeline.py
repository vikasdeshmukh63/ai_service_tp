"""
LangGraph nodes for chunking, embedding, and vector storage (placeholders).
Wire `langgraph.graph.StateGraph` here once vector DB + embeddings are configured.
"""

from __future__ import annotations

from logging import Logger

# Placeholder imports for when you implement the graph:
# from langgraph.graph import END, START, StateGraph
# from langchain_openai import OpenAIEmbeddings
# from src.ai_workflows.state import RagGraphState


async def run_embedding_placeholder_stub(log: Logger) -> None:
    """No-op stand-in for embedding + vector upsert."""
    log.debug("RAG embedding stub — connect OpenAI embeddings + vector store here.")
