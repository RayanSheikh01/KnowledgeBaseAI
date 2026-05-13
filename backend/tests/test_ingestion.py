import uuid

import pytest
from langchain_core.documents import Document
from sqlalchemy import select

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.ingestion import ingest_documents
from app.rag.store import get_vector_store


@pytest.mark.asyncio
async def test_ingest_writes_registry_and_chunks():
    docs = [
        Document(
            page_content=f"This is a test document. {uuid.uuid4().hex}",
            metadata={"source": "test.txt", "source_type": "text"},
        )
    ]
    title = "Test Document"
    source_type = "text"
    source_uri = "test.txt"

    store = get_vector_store()
    try:
        doc_id, chunk_count = await ingest_documents(docs, title, source_type, source_uri)

        async with SessionLocal() as session:
            result = await session.execute(
                select(DocumentRegistry).where(DocumentRegistry.id == doc_id)
            )
            row = result.scalar_one_or_none()

        assert row is not None
        assert row.title == title
        assert row.source_type == source_type
        assert row.source_uri == source_uri
        assert row.chunk_count == chunk_count

        stored = await store.asimilarity_search("test document", k=chunk_count)
        assert len(stored) == chunk_count
        for chunk in stored:
            assert chunk.metadata["document_id"] == str(doc_id)
            assert "chunk_index" in chunk.metadata
    finally:
        await store.adelete_collection()


@pytest.mark.asyncio
async def test_ingest_duplicates_documents():
    docs = [
        Document(
            page_content=f"This is a duplicate document. {uuid.uuid4().hex}",
            metadata={"source": "duplicate.txt", "source_type": "text"},
        )
    ]
    title = "Duplicate Document"
    source_type = "text"
    source_uri = "duplicate.txt"

    store = get_vector_store()
    try:
        doc_id_1, _ = await ingest_documents(docs, title, source_type, source_uri)
        doc_id_2, chunk_count_2 = await ingest_documents(docs, title, source_type, source_uri)

        assert doc_id_1 == doc_id_2
        assert chunk_count_2 == 0
    finally:
        await store.adelete_collection()
