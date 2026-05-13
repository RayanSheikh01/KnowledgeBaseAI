from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from sqlalchemy import create_engine, text

from app.config import get_settings
from app.rag.store import get_vector_store

_bm25_cache: BM25Retriever | None = None


def _load_all_chunks_as_documents() -> list[Document]:
    settings = get_settings()
    engine = create_engine(settings.sync_database_url)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT document, cmetadata FROM langchain_pg_embedding")
        ).all()
    return [Document(page_content=row[0], metadata=row[1] or {}) for row in rows]


def get_bm25_retriever(k: int = 10) -> BM25Retriever:
    global _bm25_cache
    if _bm25_cache is None:
        docs = _load_all_chunks_as_documents()
        if not docs:
            docs = [Document(page_content="", metadata={})]
        _bm25_cache = BM25Retriever.from_documents(docs, k=k)
    _bm25_cache.k = k
    return _bm25_cache


def invalidate_bm25_cache() -> None:
    global _bm25_cache
    _bm25_cache = None


def get_hybrid_retriever(k: int = 6) -> EnsembleRetriever:
    vec = get_vector_store().as_retriever(search_kwargs={"k": k})
    bm = get_bm25_retriever(k=k)
    return EnsembleRetriever(retrievers=[vec, bm], weights=[0.5, 0.5])
