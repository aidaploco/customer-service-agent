from __future__ import annotations

import psycopg
from pgvector.psycopg import register_vector_async
from psycopg_pool import AsyncConnectionPool

from config import get_settings
from utils.logger import get_logger

_logger = get_logger(__name__)

_pool: AsyncConnectionPool | None = None


async def _configure_conn(conn: psycopg.AsyncConnection) -> None:
    await register_vector_async(conn)


async def init_pg_pool() -> None:
    """Open the shared async connection pool. Call once at startup."""
    global _pool
    settings = get_settings()
    _pool = AsyncConnectionPool(
        settings.postgres_url,
        max_size=settings.postgres_pool_size,
        configure=_configure_conn,
        open=False,
    )
    await _pool.open()
    _logger.info("Postgres pool opened (max_size=%d)", settings.postgres_pool_size)


async def close_pg_pool() -> None:
    """Close the pool gracefully. Call on shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Postgres pool not initialized — call init_pg_pool() first")
    return _pool


async def init_db() -> None:
    """Create the pgvector extension, knowledge_chunks table, and HNSW index if absent."""
    url = get_settings().postgres_url
    async with await psycopg.AsyncConnection.connect(url, autocommit=True) as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await register_vector_async(conn)
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id          SERIAL  PRIMARY KEY,
                source      TEXT    NOT NULL,
                chunk_index INTEGER NOT NULL,
                content     TEXT    NOT NULL,
                source_hash TEXT    NOT NULL,
                embedding   vector({get_settings().embedding_dim}),
                UNIQUE (source, chunk_index)
            )
        """)
        # HNSW: no training step needed, good recall, fast at query time
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx
            ON knowledge_chunks
            USING hnsw (embedding vector_cosine_ops)
        """)


async def hash_matches(source: str, file_hash: str) -> bool:
    """Return True if at least one chunk for source is stored with this exact hash."""
    url = get_settings().postgres_url
    async with await psycopg.AsyncConnection.connect(url) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT 1 FROM knowledge_chunks WHERE source = %s AND source_hash = %s LIMIT 1",
                (source, file_hash),
            )
            return await cur.fetchone() is not None


async def replace_source_chunks(source: str, records: list[dict]) -> None:
    """Atomically replace all chunks for source. DELETE + INSERT run in one transaction."""
    url = get_settings().postgres_url
    async with await psycopg.AsyncConnection.connect(url) as conn:
        await register_vector_async(conn)
        await conn.execute("DELETE FROM knowledge_chunks WHERE source = %s", (source,))
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO knowledge_chunks (source, chunk_index, content, source_hash, embedding)
                VALUES (%(source)s, %(chunk_index)s, %(content)s, %(source_hash)s, %(embedding)s)
                """,
                records,
            )


async def search_chunks(query_embedding: list[float], top_k: int = 5) -> list[str]:
    """Return top-k chunk contents nearest to query_embedding by cosine distance."""
    async with _get_pool().connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT content FROM knowledge_chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                (query_embedding, top_k),
            )
            rows = await cur.fetchall()
    return [row[0] for row in rows]
