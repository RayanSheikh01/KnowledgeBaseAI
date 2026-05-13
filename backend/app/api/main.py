from app.api.ingest import ingest_documents, router
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(router)