import uuid

import pytest
from langchain_core.documents import Document
from sqlalchemy import delete

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.chain import build_chain
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

    chain = build_chain()
    result = await chain.ainvoke(
        {"input": "How fast can a blue marlin swim?"},
        config={"configurable": {"session_id": str(uuid.uuid4())}},
    )

    assert "context" in result
    assert any("blue marlin" in d.page_content.lower() for d in result["context"])
    assert isinstance(result["answer"], str)
    assert "80" in result["answer"]


@pytest.mark.asyncio
async def test_history_aware_chain_persists_messages():
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

    chain = build_chain()
    session_id = str(uuid.uuid4())

    result = await chain.ainvoke(
        {"input": "How fast can a blue marlin swim?"},
        config={"configurable": {"session_id": session_id}},
    )
    assert isinstance(result["answer"], str)

    from app.rag.chain import PostgresChatMessageHistory, _psycopg_connection

    history = PostgresChatMessageHistory(
        "message_store", session_id, sync_connection=_psycopg_connection
    )
    messages = history.messages
    assert len(messages) > 0
    assert any("How fast can a blue marlin swim?" in m.content for m in messages)
