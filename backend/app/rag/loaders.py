
from langchain_core.documents import Document


def load_bytes(data: bytes, filename: str) -> list[Document]:
    # decode utf8
    text = data.decode("utf-8", errors="replace")
    doc = Document(
        page_content=text,
        metadata={"source": filename
                  , "source_type": "text"},
    )
    return [doc]