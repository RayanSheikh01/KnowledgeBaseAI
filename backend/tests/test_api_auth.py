import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.auth import require_app_token


def make_app() -> FastAPI:
    app = FastAPI()

    @app.get("/secret", dependencies=[Depends(require_app_token)])
    async def secret():
        return {"ok": True}

    return app


@pytest.mark.asyncio
async def test_missing_token_returns_401():
    app = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/secret")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_correct_token_returns_200():
    app = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/secret", headers={"X-App-Token": "dev-token"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_wrong_token_returns_401():
    app = make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/secret", headers={"X-App-Token": "nope"})
    assert response.status_code == 401
