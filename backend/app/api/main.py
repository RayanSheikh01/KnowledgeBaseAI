from app.api.ingest import router as documents_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(documents_router)