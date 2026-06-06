from sqlmodel import SQLModel, create_engine

from app.config import get_settings
from app import models  # noqa: F401


settings = get_settings()
engine = create_engine(settings.resolved_database_url, connect_args={"check_same_thread": False})


def ensure_runtime_directories() -> None:
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)


def initialize_database() -> None:
    ensure_runtime_directories()
    SQLModel.metadata.create_all(engine)
