import pytest

@pytest.mark.asyncio
async def test_list_documents_returns_inserted(client):
    from sqlalchemy import delete

    from app.db.models import DocumentRegistry
    from app.db.session import SessionLocal
    from app.rag.ingestion import ingest_documents
    from app.rag.loaders import load_bytes

    async with SessionLocal() as session:
        await session.execute(delete(DocumentRegistry))
        await session.commit()

    data = b"Hello world"
    docs = load_bytes(data, filename="hello.txt")
    await ingest_documents(docs, title="Hello Doc", source_type="text", source_uri=None)

    response = await client.get(
        "/documents",
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Hello Doc"

@pytest.mark.asyncio
async def test_delete_document_removes_chunks(client):
    from sqlalchemy import delete

    from app.db.models import DocumentRegistry
    from app.db.session import SessionLocal
    from app.rag.ingestion import ingest_documents
    from app.rag.loaders import load_bytes
    from app.rag.store import get_vector_store

    store = get_vector_store()
    try:
        await store.adelete_collection()
    except Exception:
        pass

    async with SessionLocal() as session:
        await session.execute(delete(DocumentRegistry))
        await session.commit()

    data = b"Hello world"
    docs = load_bytes(data, filename="hello.txt")
    document_id, chunk_count = await ingest_documents(docs, title="Hello Doc", source_type="text", source_uri=None)
    assert chunk_count > 0

    response = await client.delete(
        f"/documents/{document_id}",
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200

    # Verify chunks are deleted
    results = await store.asimilarity_search("Hello", k=10)
    assert len(results) == 0