import pytest


@pytest.mark.asyncio
async def test_ingest_text_file_returns_doc_id(client):
    response = await client.post(
        "/ingest/file",
        files={"file": ("test.txt", b"This is a test document.", "text/plain")},
        data={"title": "Test Document"},
        headers={"X-App-Token": "dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "chunk_count" in data
