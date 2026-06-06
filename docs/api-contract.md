# API Contract

Base URL:

```txt
http://localhost:8000
```

## Foundation

### GET /health

Returns backend liveness.

Response:

```json
{
  "status": "ok",
  "service": "if-land-backend",
  "version": "0.1.0"
}
```

### GET /ready

Returns backend readiness.

Response:

```json
{
  "status": "ready",
  "database": "ok",
  "uploads": "ok"
}
```

### Static Uploads

Uploaded files will be served from:

```txt
/uploads/{filename}
```
