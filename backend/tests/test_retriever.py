import pytest
from langchain_core.documents import Document
from sqlalchemy import delete

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.ingestion import ingest_documents
from app.rag.store import get_vector_store


async def _clean_db():
    store = get_vector_store()
    try:
        await store.adelete_collection()
    except Exception:
        pass
    async with SessionLocal() as session:
        await session.execute(delete(DocumentRegistry))
        await session.commit()


@pytest.mark.asyncio
async def test_ensemble_returns_keyword_and_semantic_hits():
    from app.rag.retriever import get_hybrid_retriever

    await _clean_db()

    bm25_doc = Document(
        page_content="the elephant is large",
        metadata={"source": "bm25.txt", "source_type": "text"},
    )
    semantic_doc = Document(
        page_content="the eiffel tower is in paris",
        metadata={"source": "semantic.txt", "source_type": "text"},
    )
    irrelevant_doc = Document(
        page_content="kitchen sink unrelated",
        metadata={"source": "noise.txt", "source_type": "text"},
    )

    await ingest_documents([bm25_doc], title="BM25 Doc", source_type="text", source_uri=None)
    await ingest_documents(
        [semantic_doc], title="Semantic Doc", source_type="text", source_uri=None
    )
    await ingest_documents(
        [irrelevant_doc], title="Irrelevant Doc", source_type="text", source_uri=None
    )

    retriever = get_hybrid_retriever(k=3)
    results = await retriever.ainvoke("elephant capital city france")

    contents = [d.page_content for d in results]
    assert any("elephant" in c for c in contents), f"Missing BM25 hit; got {contents}"
    assert any("eiffel" in c for c in contents), f"Missing semantic hit; got {contents}"

    irrelevant_indices = [i for i, c in enumerate(contents) if "kitchen sink" in c]
    if irrelevant_indices:
        assert irrelevant_indices[0] == len(contents) - 1, (
            f"Irrelevant chunk should be last if present; got {contents}"
        )
