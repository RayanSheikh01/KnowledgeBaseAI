from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.rag.store import get_vector_store
from app.rag.retriever import get_hybrid_retriever


SYSTEM_PROMPT = """You are a careful research assistant. Answer the user's question using ONLY the numbered context passages below. Cite each fact with the passage number in square brackets like [1] or [2]. If the context does not contain the answer, reply exactly: "I don't know based on the provided documents." Do not invent citations.

Context:
{context}"""


def get_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        google_api_key=settings.google_api_key,
    )


def buidl_chain() -> Runnable:
    retriever = get_hybrid_retriever(k=6)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ]
    )
    document_prompt = PromptTemplate.from_template("[{chunk_index}] {page_content}")

    combine_docs = create_stuff_documents_chain(
        get_llm(), prompt, document_prompt=document_prompt
    )
    return create_retrieval_chain(retriever, combine_docs)
