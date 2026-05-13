from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings

settings = get_settings()

_engine = create_async_engine(settings.database_url, poolclass=NullPool)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(  # type: ignore[call-arg]
        model="models/gemini-embedding-001",
        google_api_key=settings.google_api_key,
    )


def get_vector_store() -> PGVector:
    # create_extension=False: the `vector` extension is created by Alembic
    # migration 0001. Letting PGVector re-issue it fails on asyncpg, which
    # rejects the multi-statement query langchain-postgres uses.
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=settings.pg_collection_name,
        connection=_engine,
        use_jsonb=True,
        async_mode=True,
        create_extension=False,
    )



