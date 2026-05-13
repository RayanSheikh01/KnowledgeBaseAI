import hashlib
import uuid

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.store import get_vector_store
from app.rag.retriever import invalidate_bm25_cache


def _content_hash(docs: list[LCDocument]) -> str:
    hasher = hashlib.sha256()
    for doc in docs:
        hasher.update(doc.page_content.encode("utf-8"))
    return hasher.hexdigest()


async def ingest_documents(
    docs: list[LCDocument],
    title: str,
    source_type: str,
    source_uri: str | None,
) -> tuple[uuid.UUID, int]:
    """Ingest documents into the vector store. Returns (document_id, chunk_count)."""
    content_hash = _content_hash(docs)



    async with SessionLocal() as session:
        existing = await session.execute(
            select(DocumentRegistry).where(DocumentRegistry.content_hash == content_hash)
        )
        existing_doc = existing.scalar_one_or_none()
        if existing_doc:
            return existing_doc.id, 0

        new_doc = DocumentRegistry(
            id=uuid.uuid4(),
            title=title,
            source_type=source_type,
            source_uri=source_uri,
            content_hash=content_hash,
            chunk_count=0,
        )
        session.add(new_doc)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            existing = await session.execute(
                select(DocumentRegistry).where(DocumentRegistry.content_hash == content_hash)
            )
            return existing.scalar_one().id, 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=150, length_function=len
        )
        chunks = splitter.split_documents(docs)
        for i, chunk in enumerate(chunks):
            chunk.metadata["document_id"] = str(new_doc.id)
            chunk.metadata["chunk_index"] = i

        vector_store = get_vector_store()
        await vector_store.aadd_documents(chunks)

        new_doc.chunk_count = len(chunks)
        await session.commit()
        invalidate_bm25_cache()
        return new_doc.id, len(chunks)
