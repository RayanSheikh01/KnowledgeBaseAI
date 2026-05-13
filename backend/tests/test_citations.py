from langchain_core.documents import Document

from app.rag.citations import extract_citations


def test_extract_returns_unique_referenced_chunks():
    docs = [
        Document(page_content="a", metadata={"document_id": "d1", "source": "s1", "page": None}),
        Document(page_content="b", metadata={"document_id": "d2", "source": "s2", "page": None}),
        Document(page_content="c", metadata={"document_id": "d3", "source": "s3", "page": None}),
    ]
    answer = "Paris is in France [1]. The Eiffel Tower is also there [1][3]."

    result = extract_citations(answer, docs)

    assert [r["n"] for r in result] == [1, 3]
    assert result[0]["source"] == "s1"
    assert result[1]["source"] == "s3"


def test_extract_ignores_out_of_range_citations():
    docs = [
        Document(page_content="a", metadata={"document_id": "d1", "source": "s1", "page": None})
    ]
    answer = "text [5]"

    result = extract_citations(answer, docs)

    assert result == []
