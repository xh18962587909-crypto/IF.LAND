from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "衣见 Backend"
    app_version: str = "0.1.0"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_url: str = "sqlite:///data/app.db"
    upload_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        if path.is_absolute():
            return path
        return self.backend_root / path

    @property
    def sqlite_path(self) -> Path:
        if not self.database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// database URLs are supported for the MVP")

        raw_path = self.database_url.replace("sqlite:///", "", 1)
        path = Path(raw_path)
        if path.is_absolute():
            return path
        return self.backend_root / path

    @property
    def resolved_database_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
