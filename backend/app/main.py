from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import ensure_runtime_directories, initialize_database


settings = get_settings()
ensure_runtime_directories()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.upload_path), name="uploads")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "if-land-backend",
        "version": settings.app_version,
    }


@app.get("/ready")
def ready() -> dict[str, str]:
    initialize_database()
    return {
        "status": "ready",
        "database": "ok",
        "uploads": "ok",
    }
