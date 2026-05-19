from unittest.mock import AsyncMock, MagicMock, patch

from agent.general.ingester import _chunk_markdown, _file_hash, ingest_changed


def test_file_hash_is_deterministic(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("hello world")
    assert _file_hash(f) == _file_hash(f)


def test_file_hash_differs_for_different_content(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("version one")
    h1 = _file_hash(f)
    f.write_text("version two")
    h2 = _file_hash(f)
    assert h1 != h2


def test_chunk_markdown_drops_standalone_headings():
    text = "# Title\n\nParagraph one.\n\n## Section\n\nParagraph two."
    assert _chunk_markdown(text) == ["Paragraph one.", "Paragraph two."]


def test_chunk_markdown_drops_empty_paragraphs():
    text = "Para one.\n\n\n\nPara two."
    assert _chunk_markdown(text) == ["Para one.", "Para two."]


def test_chunk_markdown_keeps_mixed_heading_and_body():
    text = "## Section\nBody text here."
    chunks = _chunk_markdown(text)
    assert len(chunks) == 1
    assert "Body text here." in chunks[0]


async def test_ingest_changed_skips_unchanged_files(openai_env):
    with (
        patch("agent.general.ingester.init_db", new_callable=AsyncMock),
        patch(
            "agent.general.ingester.hash_matches",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "agent.general.ingester.replace_source_chunks", new_callable=AsyncMock
        ) as mock_replace,
    ):
        await ingest_changed()
    mock_replace.assert_not_called()


async def test_ingest_changed_ingests_when_hash_differs(openai_env):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1] * 1536) for _ in range(10)]
    mock_client = MagicMock()
    mock_client.embeddings.create = AsyncMock(return_value=mock_response)

    with (
        patch("agent.general.ingester.init_db", new_callable=AsyncMock),
        patch(
            "agent.general.ingester.hash_matches",
            new_callable=AsyncMock,
            return_value=False,
        ),
        patch(
            "agent.general.ingester.replace_source_chunks", new_callable=AsyncMock
        ) as mock_replace,
        patch("agent.general.ingester.get_async_client", return_value=mock_client),
    ):
        await ingest_changed()

    assert mock_replace.call_count == 5  # one call per knowledge file
