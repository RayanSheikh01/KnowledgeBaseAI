from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.rag.chain import buidl_chain
from app.api.auth import require_app_token

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str


@router.post("/chat", dependencies=[Depends(require_app_token)])
async def chat(request: ChatRequest):
    chain = buidl_chain()
    try:
        result = await chain.ainvoke({"input": request.message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "answer": result["answer"],
        "chunk_ids": [str(d.metadata["chunk_index"]) for d in result.get("context", [])],
    }


    