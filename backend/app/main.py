from fastapi import FastAPI
from .config import get_settings

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}


settings = get_settings()

CORSMiddleware = {
    "allow_origins": settings.allowed_origins_list,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}