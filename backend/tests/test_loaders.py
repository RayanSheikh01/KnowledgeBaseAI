from pathlib import Path

import pytest

from app.rag.loaders import load_bytes

FIXTURES = Path(__file__).parent / "fixtures"

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

@pytest.mark.asyncio
async def test_load_pdf_bytes_returns_docs_with_pages():
    data = (FIXTURES / "example.pdf").read_bytes()
    docs = load_bytes(data, filename="example.pdf")
    assert len(docs) > 0
    for doc in docs:
        assert "Page" in doc.metadata["source"]
        assert doc.metadata["source_type"] == "pdf"

@pytest.mark.asyncio
async def test_load_url_returns_doc():
    url = "https://www.example.com"
    docs = load_bytes(url.encode("utf-8"), filename=url)
    assert len(docs) == 1
    assert docs[0].page_content != ""
    assert docs[0].metadata["source"] == url
    assert docs[0].metadata["source_type"] == "url"

