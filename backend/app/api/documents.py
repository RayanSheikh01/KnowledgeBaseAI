from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.future import select


from app.api.auth import require_app_token
from app.db.models import DocumentRegistry
from app.db.session import SessionLocal
from app.rag.retriever import invalidate_bm25_cache



router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(require_app_token)])

@router.get("")
async def list_documents():
    async with SessionLocal() as session:
        result = await session.execute(select(DocumentRegistry))
        documents = result.scalars().all()
        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "source_type": doc.source_type,
                "source_uri": doc.source_uri,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ]

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    async with SessionLocal() as session:
        result = await session.execute(select(DocumentRegistry).where(DocumentRegistry.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        await session.execute(
            text("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'document_id' = :doc_id"),
            {"doc_id": document_id},
        )
        await session.delete(document)
        await session.commit()
        invalidate_bm25_cache()
    return {"detail": "Document deleted"}

