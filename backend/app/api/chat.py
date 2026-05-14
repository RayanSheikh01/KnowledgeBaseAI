import json
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.auth import require_app_token
from app.rag.chain import build_chain


router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _snippet(text: str, limit: int = 240) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


@router.post("/chat", dependencies=[Depends(require_app_token)])
async def chat(request: ChatRequest) -> StreamingResponse:
    chain = build_chain()
    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator():
        retrieved_docs: list = []
        try:
            yield _sse("session", {"session_id": session_id})

            async for event in chain.astream_events(
                {"input": request.message},
                version="v2",
                config={"configurable": {"session_id": session_id}},
            ):
                kind = event["event"]
                if kind == "on_retriever_end":
                    retrieved_docs = event["data"].get("output") or []
                elif kind == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    text = getattr(chunk, "content", "") if chunk is not None else ""
                    if text:
                        yield _sse("token", {"content": text})

            citations = []
            for idx, doc in enumerate(retrieved_docs):
                meta = doc.metadata or {}
                page = meta.get("page")
                citations.append(
                    {
                        "n": idx + 1,
                        "document_id": str(meta.get("document_id", "")),
                        "source": meta.get("source"),
                        "snippet": _snippet(doc.page_content),
                        "page_number": (page + 1) if isinstance(page, int) else None,
                        "heading_path": None,
                    }
                )
            yield _sse("citations", {"citations": citations})

        except Exception as exc:
            yield _sse("error", {"message": str(exc)})
            return

        yield _sse("done", {})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
