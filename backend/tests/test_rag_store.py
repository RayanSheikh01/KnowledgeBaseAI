import pytest
from langchain_core.documents import Document

from app.rag.store import get_vector_store


@pytest.mark.asyncio
async def test_rag_store():
    store = get_vector_store()
    try:
        doc1 = Document(page_content="This is a test document.")
        doc2 = Document(page_content="This is another test document.")
        await store.aadd_documents([doc1, doc2])
        results = await store.asimilarity_search("test", k=2)
        assert {r.page_content for r in results} == {
            "This is a test document.",
            "This is another test document.",
        }
    finally:
        await store.adelete_collection()
