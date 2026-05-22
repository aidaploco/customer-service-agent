from __future__ import annotations

from agents import function_tool

from config import get_settings
from llm.openai import get_embedding
from store.vector_store import search_chunks
from utils.logger import get_logger

_logger = get_logger(__name__)


async def _search_company_info(query: str) -> str:
    try:
        embedding = await get_embedding(query)
        chunks = await search_chunks(embedding, top_k=get_settings().rag_top_k)
        if not chunks:
            return "No information found for that query. Suggest the customer visit brightloop.io or contact support."
        return "\n\n---\n\n".join(chunks)
    except Exception:
        _logger.warning("Knowledge base search failed", exc_info=True)
        return "Knowledge base search is temporarily unavailable. Suggest the customer visit brightloop.io or contact support@brightloop.io."


@function_tool
async def search_company_info(query: str) -> str:
    """
    Search Brightloop's knowledge base for general company information: history, product
    features, pricing overview, security, compliance, and SLA. Use this to answer any
    question about Brightloop that is not a billing transaction or a technical support issue.
    """
    return await _search_company_info(query)
