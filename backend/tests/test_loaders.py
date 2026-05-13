import pytest
from app.rag.loaders import load_bytes

@pytest.mark.asyncio
async def test_load_text_bytes_markdown():
    data = b"# Sample Markdown\n\nThis is a sample markdown file."
    docs = load_bytes(data, filename="sample.md")
    assert len(docs) == 1
    assert docs[0].page_content == data.decode("utf-8", errors="replace")
    assert docs[0].metadata["source"] == "sample.md"
    assert docs[0].metadata["source_type"] == "text"

@pytest.mark.asyncio
async def test_load_text_bytes_plain():
    data = load_bytes(b"hello world", filename="note.txt")
    assert len(data) == 1
    assert data[0].page_content == "hello world"
    assert data[0].metadata["source"] == "note.txt"
    assert data[0].metadata["source_type"] == "text"

