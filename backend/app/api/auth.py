from fastapi import Header, HTTPException

from app.config import get_settings


async def require_app_token(x_app_token: str | None = Header(default=None)) -> None:
    if x_app_token != get_settings().app_token:
        raise HTTPException(status_code=401, detail="invalid app token")
