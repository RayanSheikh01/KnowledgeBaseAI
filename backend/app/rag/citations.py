import re

from langchain_core.documents import Document


CITATION_RE = re.compile(r"\[(\d+)\]")


def extract_citations(answer: str, docs: list[Document]) -> list[dict]:
    """Extract cited passages from an LLM answer, in first-seen order, deduped, range-checked."""
    seen: set[int] = set()
    out: list[dict] = []
    for match in CITATION_RE.finditer(answer):
        n = int(match.group(1))
        if n in seen or n < 1 or n > len(docs):
            continue
        seen.add(n)

        doc = docs[n - 1]
        md = doc.metadata or {}
        document_id = md.get("document_id")
        chunk_index = md.get("chunk_index")
        chunk_id = (
            f"{document_id}:{chunk_index}"
            if document_id is not None and chunk_index is not None
            else None
        )

        snippet = doc.page_content[:240]
        if len(doc.page_content) > 240:
            snippet += "…"

        out.append(
            {
                "n": n,
                "chunk_id": chunk_id,
                "document_id": document_id,
                "source": md.get("source"),
                "snippet": snippet,
                "page_number": md.get("page"),
                "heading_path": md.get("heading_path"),
            }
        )
    return out
