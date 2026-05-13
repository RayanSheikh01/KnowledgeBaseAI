from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.api.auth import require_app_token
from app.rag.ingestion import ingest_documents
from app.rag.loaders import load_bytes, load_url


class IngestUrlRequest(BaseModel):
    url: str

router = APIRouter(prefix="/ingest", tags=["ingest"])
TEXT_MIMES = {"text/plain", "text/markdown", "application/octet-stream"}


@router.post("/file", dependencies=[Depends(require_app_token)])
async def ingest_file(
    file: UploadFile = File(...),
    title: str = Form(...)):
    if file.content_type not in TEXT_MIMES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    docs = load_bytes(content, filename=file.filename)
    document_id, chunk_count = await ingest_documents(
        docs, title=title, source_type="text", source_uri=None
    )
    return {"document_id": str(document_id), "chunk_count": chunk_count}


@router.post("/url", dependencies=[Depends(require_app_token)])
async def ingest_url_request(body: IngestUrlRequest):
    docs = load_url(body.url)
    document_id, chunk_count = await ingest_documents(
        docs, title=body.url, source_type="url", source_uri=body.url
    )
    return {"document_id": str(document_id), "chunk_count": chunk_count}