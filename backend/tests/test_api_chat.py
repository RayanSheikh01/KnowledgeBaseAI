import json

import pytest
from langchain_core.documents import Document
from sqlalchemy import delete
import uuid

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
    
    events = []
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            event_data = line[len("data: "):].strip()
            events.append(json.loads(event_data))
    
    final_event = events[-1]
    assert "answer" in final_event["data"]
    assert isinstance(final_event["data"]["answer"], str)
    assert "paris" in final_event["data"]["answer"].lower()

@pytest.mark.asyncio
async def test_chat_streams_tokens_then_citations_then_done(client):
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

    events = []
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            event_data = line[len("data: "):].strip()
            events.append(json.loads(event_data))

    assert len(events) >= 2
    assert events[0]["event"] == "answer_update"
    assert "paris" in events[0]["data"]["answer"].lower()
    assert events[-1]["event"] == "answer_final"
    assert "paris" in events[-1]["data"]["answer"].lower()
    assert "retrieved_docs" in events[-1]["data"]
    assert len(events[-1]["data"]["retrieved_docs"]) == 1
    assert events[-1]["data"]["retrieved_docs"][0]["source"] == "geo.txt"

async def test_chat_persists_and_session_carries(client):
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
    await ingest_documents(docs, title="Fish Facts", source_type="text", source_uri=None)

    session_id = str(uuid.uuid4())

    response = await client.post(
        "/chat",
        json={"message": "How fast can a blue marlin swim?", "session_id": session_id},
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200

    events = []
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            event_data = line[len("data: "):].strip()
            events.append(json.loads(event_data))

    final_event = events[-1]
    assert "answer" in final_event["data"]
    assert isinstance(final_event["data"]["answer"], str)
    assert "80" in final_event["data"]["answer"]