import psycopg
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable, RunnableWithMessageHistory
from langchain_core.runnables.config import run_in_executor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_postgres import PostgresChatMessageHistory

from app.config import get_settings
from app.rag.retriever import get_hybrid_retriever


SYSTEM_PROMPT = """You are a careful research assistant. Answer the user's question using ONLY the numbered context passages below. Cite each fact with the passage number in square brackets like [1] or [2]. If the context does not contain the answer, reply exactly: "I don't know based on the provided documents." Do not invent citations.

Context:
{context}"""

CONTEXTUALIZE_PROMPT = (
    "Given the chat history and the latest user question, rewrite the question "
    "to be standalone. Do NOT answer it; only output the rewritten question."
)


_settings = get_settings()
# psycopg.connect wants a libpq-style URL; strip SQLAlchemy's "+psycopg" driver suffix.
_libpq_url = _settings.sync_database_url.replace("postgresql+psycopg://", "postgresql://")
_psycopg_connection = psycopg.connect(_libpq_url)
PostgresChatMessageHistory.create_tables(_psycopg_connection, "message_store")


class _SyncBackedPostgresChatMessageHistory(PostgresChatMessageHistory):
    """Routes async history ops through the sync connection (thread pool).

    The vanilla PostgresChatMessageHistory requires an async psycopg connection
    for aget/aadd; opening one at module import is impractical because
    AsyncConnection.connect must be awaited. We only need a sync connection;
    async callers pay one threadpool hop.
    """

    async def aget_messages(self) -> list[BaseMessage]:
        return await run_in_executor(None, self.get_messages)

    async def aadd_messages(self, messages):
        await run_in_executor(None, self.add_messages, list(messages))

    async def aclear(self):
        await run_in_executor(None, self.clear)


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=_settings.google_api_key,
    )


def _get_session_history(session_id: str) -> PostgresChatMessageHistory:
    return _SyncBackedPostgresChatMessageHistory(
        "message_store", session_id, sync_connection=_psycopg_connection
    )


def build_chain() -> Runnable:
    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CONTEXTUALIZE_PROMPT),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    document_prompt = PromptTemplate.from_template("[{chunk_index}] {page_content}")

    history_aware_retriever = create_history_aware_retriever(
        llm=get_llm(),
        retriever=get_hybrid_retriever(k=6),
        prompt=contextualize_prompt,
    )

    combine_docs = create_stuff_documents_chain(
        get_llm(), qa_prompt, document_prompt=document_prompt
    )

    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs)

    return RunnableWithMessageHistory(
        rag_chain,
        _get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
