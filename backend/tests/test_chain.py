import pytest
from langchain_core.documents import Document
from sqlalchemy import delete

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.chain import build_naive_chain
from app.rag.ingestion import ingest_documents
from app.rag.store import get_vector_store


@pytest.mark.asyncio
async def test_chain_invokes_with_context():
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
            page_content="The blue marlin can swim at speeds of up to 80 mph.",
            metadata={"source": "fish.txt"},
        )
    ]
    _document_id, chunk_count = await ingest_documents(
        docs, title="Fish Facts", source_type="text", source_uri=None
    )
    assert chunk_count > 0

    chain = build_naive_chain()
    result = await chain.ainvoke({"input": "How fast can a blue marlin swim?"})

    assert "context" in result
    assert any("blue marlin" in d.page_content.lower() for d in result["context"])
    assert isinstance(result["answer"], str)
    assert "80" in result["answer"]
