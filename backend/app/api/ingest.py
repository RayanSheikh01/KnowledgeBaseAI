from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.auth import require_app_token
from app.rag.ingestion import ingest_documents
from app.rag.loaders import load_bytes, load_url


class IngestUrlRequest(BaseModel):
    url: str


router = APIRouter(prefix="/ingest", tags=["ingest"])
TEXT_MIMES = {"text/plain", "text/markdown", "application/octet-stream"}


@router.post("/file", dependencies=[Depends(require_app_token)])
async def ingest_file(file: UploadFile = File(...)):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")

    name = file.filename or ""
    lower = name.lower()
    mime = file.content_type or ""
    is_pdf = lower.endswith(".pdf") or mime == "application/pdf"
    is_text = (
        lower.endswith(".txt")
        or lower.endswith(".md")
        or mime in TEXT_MIMES
    )
    if not (is_pdf or is_text):
        raise HTTPException(status_code=400, detail="unsupported file type")

    docs = load_bytes(data, filename=name)
    source_type = "pdf" if is_pdf else "text"
    document_id, chunk_count = await ingest_documents(
        docs, title=name, source_type=source_type, source_uri=name
    )
    return {"document_id": str(document_id), "chunk_count": chunk_count}


@router.post("/url", dependencies=[Depends(require_app_token)])
async def ingest_url_request(body: IngestUrlRequest):
    docs = load_url(body.url)
    document_id, chunk_count = await ingest_documents(
        docs, title=body.url, source_type="url", source_uri=body.url
    )
    return {"document_id": str(document_id), "chunk_count": chunk_count}
