import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.rag.chain import build_chain
from app.api.auth import require_app_token

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


def _sse(event: str, data: dict) -> str:
    payload = {"event": event, "data": data}
    return f"event: message\ndata: {json.dumps(payload)}\n\n"

@router.post("/chat", dependencies=[Depends(require_app_token)])
async def chat(request: ChatRequest) -> StreamingResponse:
    chain = build_chain()
    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator():
        answer_buf: list[str] = []
        retrieved_docs: list[dict] = []
        try:
            async for event in chain.astream_events({"input": request.message}, version="v2", config={"configurable": {"session_id": session_id}}):
                yield _sse("session", {"session_id": session_id})
                kind = event["event"]
                if kind == "on_retriever_end":
                    docs = event["data"].get("output") or []
                    retrieved_docs = [
                        {
                            "source": d.metadata.get("source"),
                            "document_id": d.metadata.get("document_id"),
                            "chunk_index": d.metadata.get("chunk_index"),
                        }
                        for d in docs
                    ]
                elif kind == "on_chat_model_stream":
                    chunk = event["data"].get("chunk")
                    text = getattr(chunk, "content", "") if chunk is not None else ""
                    if text:
                        answer_buf.append(text)
                        yield _sse("answer_update", {"answer": "".join(answer_buf)})


        except Exception as e:
            yield _sse("error", {"message": str(e)})
            return

        yield _sse(
            "answer_final",
            {"answer": "".join(answer_buf), "retrieved_docs": retrieved_docs}
        )

        yield _sse("done", {"answer": "".join(answer_buf), "session_id": session_id})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
        








    