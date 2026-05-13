import pytest


@pytest.mark.asyncio
async def test_ingest_text_file_returns_doc_id(client):
    response = await client.post(
        "/ingest/file",
        files={"file": ("test.txt", b"This is a test document.", "text/plain")},
        data={"title": "Test Document"},
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "chunk_count" in data


@pytest.mark.asyncio
async def test_ingest_url(client):
    from sqlalchemy import delete

    from app.db.models import DocumentRegistry
    from app.db.session import SessionLocal
    from app.rag.store import get_vector_store

    url = "https://www.example.com"

    async with SessionLocal() as session:
        await session.execute(delete(DocumentRegistry).where(DocumentRegistry.source_uri == url))
        await session.commit()
    store = get_vector_store()
    try:
        await store.adelete_collection()
    except Exception:
        pass

    response = await client.post(
        "/ingest/url",
        json={"url": url},
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "chunk_count" in data
    assert data["chunk_count"] > 0