from __future__ import annotations

import hashlib
from pathlib import Path

from config import get_settings
from llm.openai import get_async_client
from store.vector_store import hash_matches, init_db, replace_source_chunks
from utils.logger import get_logger

_logger = get_logger(__name__)

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _chunk_markdown(text: str) -> list[str]:
    """Split markdown into paragraph chunks, dropping standalone heading lines."""
    chunks = []
    for paragraph in text.split("\n\n"):
        stripped = paragraph.strip()
        if not stripped:
            continue
        if all(line.startswith("#") for line in stripped.splitlines()):
            continue
        chunks.append(stripped)
    return chunks


async def ingest_changed() -> None:
    """On startup: initialise the DB schema, then embed and store any new or changed files."""
    await init_db()

    client = get_async_client()
    md_files = sorted(_KNOWLEDGE_DIR.glob("*.md"))

    for md_file in md_files:
        file_hash = _file_hash(md_file)

        if await hash_matches(md_file.name, file_hash):
            _logger.debug("knowledge unchanged source=%s", md_file.name)
            continue

        chunks = _chunk_markdown(md_file.read_text())
        response = await client.embeddings.create(model=get_settings().embedding_model, input=chunks)
        embeddings = [item.embedding for item in response.data]

        records = [
            {
                "source": md_file.name,
                "chunk_index": i,
                "content": chunk,
                "source_hash": file_hash,
                "embedding": embedding,
            }
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]

        await replace_source_chunks(md_file.name, records)
        _logger.info("knowledge ingested source=%s chunks=%d", md_file.name, len(chunks))
