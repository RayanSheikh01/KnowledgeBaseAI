import uuid

import pytest
from sqlalchemy import select

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal


@pytest.mark.asyncio
async def test_document_registry_round_trip():
    async with SessionLocal() as s:
        registry = DocumentRegistry(
            title="Test",
            source_type="text",
            source_uri="t.txt",
            content_hash=f"hash-{uuid.uuid4().hex}",
        )
        s.add(registry)
        await s.commit()
        await s.refresh(registry)

        assert isinstance(registry.id, uuid.UUID)
        assert registry.created_at is not None

        result = await s.execute(
            select(DocumentRegistry).where(DocumentRegistry.id == registry.id)
        )
        row = result.scalar_one()
        assert row.title == "Test"
        assert row.source_type == "text"
