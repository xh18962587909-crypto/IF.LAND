from pathlib import Path

from fastapi.testclient import TestClient

from app.db import initialize_database
from app.main import app


client = TestClient(app)


def test_health_endpoint_reports_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "if-land-backend",
        "version": "0.1.0",
    }


def test_ready_endpoint_initializes_sqlite_database():
    initialize_database()

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "ok"


def test_cors_allows_vite_frontend_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_uploads_are_served_as_static_files():
    uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    sample_file = uploads_dir / "static-health-check.txt"
    sample_file.write_text("uploads-ok", encoding="utf-8")

    response = client.get("/uploads/static-health-check.txt")

    assert response.status_code == 200
    assert response.text == "uploads-ok"
