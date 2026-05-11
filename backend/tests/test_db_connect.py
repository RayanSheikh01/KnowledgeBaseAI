import pytest
from sqlalchemy import text

from app.db.session import SessionLocal


@pytest.mark.asyncio
async def test_db_connection():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
