from __future__ import annotations

from agents import function_tool

from config import get_settings
from llm.openai import get_async_client
from store.vector_store import search_chunks


async def _search_company_info(query: str) -> str:
    client = get_async_client()
    response = await client.embeddings.create(
        model=get_settings().embedding_model, input=query
    )
    chunks = await search_chunks(response.data[0].embedding, top_k=4)
    if not chunks:
        return "No information found for that query. Suggest the customer visit brightloop.io or contact support."
    return "\n\n---\n\n".join(chunks)


@function_tool
async def search_company_info(query: str) -> str:
    """
    Search Brightloop's knowledge base for general company information: history, product
    features, pricing overview, security, compliance, and SLA. Use this to answer any
    question about Brightloop that is not a billing transaction or a technical support issue.
    """
    return await _search_company_info(query)
