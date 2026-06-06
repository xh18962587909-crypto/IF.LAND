# 衣见 Backend

FastAPI backend for the hackathon MVP.

## Run Locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the API docs:

```txt
http://localhost:8000/docs
```

## Foundation Endpoints

```txt
GET /health
GET /ready
GET /uploads/{filename}
```

## Frontend Base URL

```txt
VITE_API_BASE_URL=http://localhost:8000
```
