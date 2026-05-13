import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document


def load_bytes(data: bytes, filename: str) -> list[Document]:
    if filename.startswith("http://") or filename.startswith("https://"):
        return load_url(filename)

    if filename.lower().endswith(".pdf"):
        return _load_pdf_bytes(data, filename)

    text = data.decode("utf-8", errors="replace")2
    return [
        Document(
            page_content=text,
            metadata={"source": filename, "source_type": "text"},
        )
    ]


def load_url(url: str) -> list[Document]:
    loader = WebBaseLoader(
        url,
        requests_kwargs={
            "headers": {"User-Agent": "KnowledgeBaseAI/0.1"},
            "timeout": 20,
        },
    )
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = url
        doc.metadata["source_type"] = "url"
    return docs


def _load_pdf_bytes(data: bytes, filename: str) -> list[Document]:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        raw = loader.load()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    docs: list[Document] = []
    for page in raw:
        page_number = page.metadata.get("page", 0) + 1
        docs.append(
            Document(
                page_content=page.page_content,
                metadata={
                    "source": f"{filename} - Page {page_number}",
                    "source_type": "pdf",
                },
            )
        )
    return docs
