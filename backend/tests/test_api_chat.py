import pytest
from langchain_core.documents import Document
from sqlalchemy import delete

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.ingestion import ingest_documents
from app.rag.store import get_vector_store


@pytest.mark.asyncio
async def test_chat_returns_answer(client):
    store = get_vector_store()
    try:
        await store.adelete_collection()
    except Exception:
        pass
    async with SessionLocal() as session:
        await session.execute(delete(DocumentRegistry))
        await session.commit()

    docs = [
        Document(
            page_content="Paris is the capital of France.",
            metadata={"source": "geo.txt"},
        )
    ]
    await ingest_documents(docs, title="Geography", source_type="text", source_uri=None)

    response = await client.post(
        "/chat",
        json={"message": "What is the capital of France?"},
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert "paris" in data["answer"].lower()
