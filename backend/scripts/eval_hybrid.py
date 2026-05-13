import asyncio

from langchain_core.documents import Document

from app.rag.ingestion import ingest_documents
from app.rag.retriever import get_hybrid_retriever, invalidate_bm25_cache
from app.rag.store import get_vector_store


CORPUS: list[tuple[str, str]] = [
    (
        "Blue Marlin",
        "The blue marlin is a large fish found in tropical oceans. It can swim at speeds of up to 80 mph and is one of the fastest fish in the world.",
    ),
    (
        "Capital of France",
        "Paris is the capital city of France. It is famous for landmarks such as the Eiffel Tower and the Louvre museum.",
    ),
    (
        "Python Language",
        "Python is a high-level programming language created by Guido van Rossum and first released in 1991. It emphasizes code readability.",
    ),
    (
        "Great Wall",
        "The Great Wall of China stretches over 13,000 miles and was built over many centuries to protect ancient Chinese states from invasions.",
    ),
    (
        "Photosynthesis",
        "Photosynthesis is the process by which green plants use sunlight to convert carbon dioxide and water into glucose and oxygen.",
    ),
]


QUESTIONS: list[tuple[str, str]] = [
    ("How fast can a blue marlin swim?", "80"),
    ("What is the capital of France?", "Paris"),
    ("Who created the Python programming language?", "Guido van Rossum"),
    ("How long is the Great Wall of China?", "13,000"),
    ("What do plants produce during photosynthesis?", "oxygen"),
]


async def _seed_corpus() -> None:
    for title, content in CORPUS:
        docs = [Document(page_content=content, metadata={"source": title})]
        await ingest_documents(docs, title=title, source_type="text", source_uri=None)


def _hit(docs, expected: str) -> bool:
    needle = expected.lower()
    return any(needle in d.page_content.lower() for d in docs)


async def main() -> None:
    await _seed_corpus()
    invalidate_bm25_cache()

    vector_retriever = get_vector_store().as_retriever(search_kwargs={"k": 6})
    hybrid = get_hybrid_retriever(k=6)

    print(f"{'Q#':<3} {'vector':<8} {'hybrid':<8} question")
    print("-" * 80)
    v_total = h_total = 0
    for i, (question, expected) in enumerate(QUESTIONS, start=1):
        v_docs = await vector_retriever.ainvoke(question)
        h_docs = await hybrid.ainvoke(question)
        v = _hit(v_docs, expected)
        h = _hit(h_docs, expected)
        v_total += int(v)
        h_total += int(h)
        print(
            f"{i:<3} "
            f"{'HIT' if v else 'MISS':<8} "
            f"{'HIT' if h else 'MISS':<8} "
            f"{question}  (expected: {expected!r})"
        )

    print("-" * 80)
    print(f"vector hit rate: {v_total}/{len(QUESTIONS)}")
    print(f"hybrid hit rate: {h_total}/{len(QUESTIONS)}")


if __name__ == "__main__":
    asyncio.run(main())
