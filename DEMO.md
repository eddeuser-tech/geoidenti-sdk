# GeoIdenti SDK Demo Guide

This guide explains how to run the two GeoIdenti SDK demo scripts against a live engine instance.
Both scripts use only the public `GeoIdenti` SDK client — no internal engine imports, no direct Qdrant access.

## Purpose

### `demo.py` — Quick API Walkthrough (analyst key)

Exercises the full read + write surface of the SDK in six sections:

| Section | Operation |
|---|---|
| 1 — Health | `client.health()` — unauthenticated liveness check |
| 2 — Status | `client.status()` — authenticated role/user check |
| 3 — Analyze | `client.analyze(image_url)` × 2 Unsplash portrait URLs |
| 4 — Label | `client.label_identity(vector_id, name)` on the first result |
| 5 — Search | `client.search(identity_name=..., limit=5)` filter search |
| 6 — Hybrid | `client.search_vector(face_vector=..., semantic_query=...)` hybrid search |

### `integration/image_url_demo.py` — Full Pipeline (admin key)

Runs a complete biometric identity pipeline across 6 sample URLs from `integration/sample_images.json`:

| Pass | Operation |
|---|---|
| 1 — Analyze | All 6 URLs through `client.analyze()` with sidecar metadata |
| 2 — Label | Explicit label assignment for the 3 sidecar-tagged identities |
| 3 — Propagate | `client.propagate_from_image()` post-processing pass — spreads labels to similar unlabeled vectors |
| 4 — Search | `client.search(identity_name=...)` validation per labeled identity |
| 5 — Hybrid | `client.search_vector(face_vector=..., semantic_query="family outdoor")` |
| 6 — Summary | Table of image_url → city → identity_name → vector_id |

---

## Prerequisites

- Python 3.9+
- GeoIdenti engine running (Docker Compose — see below)
- `geoidenti-sdk` installed:
  ```bash
  pip install geoidenti-sdk
  # or from source:
  pip install -e /path/to/geoidenti-sdk
  ```

### Start the Engine (Docker Compose)

```bash
# From the engine repository root
docker compose up -d

# Confirm services are healthy
docker compose ps

# Wait for the API to be ready
sleep 10

# Verify
curl http://localhost:8000/health
```

---

## Auth Setup

`demo.py` requires an **analyst-level** JWT. `integration/image_url_demo.py` requires an **admin-level** JWT (the label and propagate endpoints enforce admin role).

### Generate a token via the engine

```bash
# From the engine repository root
DEBUG=true SECRET_KEY=development-secret-key-change-in-production JWT_ALGORITHM=HS256 \
  .venv/bin/python3.11 - <<'PY'
from src.auth import TokenManager
# Analyst token (demo.py)
print("ANALYST:", TokenManager.create_token({'sub': 'demo-user', 'role': 'analyst'}))
# Admin token (image_url_demo.py)
print("ADMIN:  ", TokenManager.create_token({'sub': 'demo-admin', 'role': 'admin'}))
PY
```

### Configure environment variables

```bash
# Required for both scripts
export GEOIDENTI_API_KEY="<your-jwt>"

# Optional — defaults to https://api.geoidenti.com/v1
export GEOIDENTI_BASE_URL="http://localhost:8000/v1"
```

| Variable | Required | Default |
|---|---|---|
| `GEOIDENTI_API_KEY` | Yes | — |
| `GEOIDENTI_BASE_URL` | No | `https://api.geoidenti.com/v1` |

---

## Running `demo.py`

```bash
cd /path/to/geoidenti-sdk

export GEOIDENTI_API_KEY="<your-analyst-jwt>"
export GEOIDENTI_BASE_URL="http://localhost:8000/v1"

python3 demo.py
```

### Expected output

```
🚀 GeoIdenti SDK — Quick Demo
============================================================
Analyst-level walkthrough:
  1. Health check    4. Label identity
  2. API status      5. Search by name
  3. Analyze images  6. Hybrid search
============================================================

============================================================
🎯 Section 1 — Health Check
============================================================
✅ Status:  healthy
   Version: 1.x.x
   Time:    2026-04-18T...

============================================================
🎯 Section 3 — Analyze Images
============================================================

🔍 [1] https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400
   ✅ vector_id:        vec-xxxxxxxx-...
   📍 city:             Seattle
   📍 country:          USA
   🔍 inferred_identity: False

...

============================================================
🎯 Demo Complete
============================================================
🎉 All sections finished.
```

---

## Running `integration/image_url_demo.py`

```bash
cd /path/to/geoidenti-sdk

export GEOIDENTI_API_KEY="<your-admin-jwt>"
export GEOIDENTI_BASE_URL="http://localhost:8000/v1"

python3 integration/image_url_demo.py
```

### Expected output (abbreviated)

```
🚀 GeoIdenti SDK — Image URL Pipeline Demo
============================================================
...

🎯 Pass 1 — Analyze Images
============================================================
Submitting 6 URL(s) to POST /v1/analyze...

🔍 [1/6] https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400
   ✅ vector_id:        vec-xxxxxxxx-...
   📍 city:             Seattle
   🔍 inferred_identity: False

...

🎯 Pass 3 — Propagation Pass
============================================================
✅ 'Alex Rivera' — updated_count=2, threshold=0.85
✅ 'Jamie Chen'  — updated_count=1, threshold=0.85
ℹ️  'Morgan Lee'  — updated_count=0, threshold=0.85

...

🎯 Summary
============================================================
  image_url                                      city             identity_name          vector_id
  ...
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `EnvironmentError: GEOIDENTI_API_KEY is not set` | `export GEOIDENTI_API_KEY="<token>"` |
| `401 Unauthorized` | Token expired or wrong role — regenerate (analyst for demo.py, admin for image_url_demo.py) |
| `ConnectionRefusedError` / `Connection refused` | Start the engine: `docker compose up -d` then `sleep 10` |
| `analyze()` returns no `vector_id` / empty string | Image URL must be publicly reachable — test with `curl -I <url>` |
| `propagate updated_count = 0` for all identities | At least one analyze pass with that identity must have run first; check Pass 1 completed successfully |
| `search()` returns empty list after label | Allow 1–2 seconds for the engine to index the labeled vector, then rerun |
| `FileNotFoundError: sample_images.json` | Run from the repo root: `python3 integration/image_url_demo.py`, not from inside `integration/` |

---

## curl Equivalents

All SDK methods map directly to engine REST endpoints. Below is a side-by-side reference.

Replace `$TOKEN` with your JWT and `$BASE` with `http://localhost:8000`.

### Health check

```python
# SDK
client.health()
```
```bash
# curl
curl "$BASE/health"
```

### Analyze an image

```python
# SDK
client.analyze(
    "https://example.com/photo.jpg",
    identity_name="Alex Rivera",
    relationship="colleague",
)
```
```bash
# curl
curl -s -X POST "$BASE/v1/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/photo.jpg",
       "identity_name": "Alex Rivera",
       "relationship": "colleague"}'
```

### Label an identity

```python
# SDK
client.label_identity("vec-12345", "Alex Rivera")
```
```bash
# curl
curl -s -X PATCH "$BASE/v1/label" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vector_id": "vec-12345", "name": "Alex Rivera"}'
```

### Filter search

```python
# SDK
client.search(identity_name="Alex Rivera", city="Seattle", limit=5)
```
```bash
# curl
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE/v1/search?identity_name=Alex+Rivera&city=Seattle&limit=5"
```

### Hybrid face + semantic search

```python
# SDK
client.search_vector(
    face_vector=[...],          # 128-dim list from analyze()
    semantic_query="outdoor portrait",
    face_weight=0.6,
    limit=5,
)
```
```bash
# curl
curl -s -X POST "$BASE/v1/search/vector" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"face_vector": [0.1, 0.2, ...],
       "semantic_query": "outdoor portrait",
       "face_weight": 0.6,
       "limit": 5}'
```

### Propagate label from image

```python
# SDK
client.propagate_from_image(
    "https://example.com/photo.jpg",
    "Alex Rivera",
    similarity_threshold=0.85,
    dry_run=False,
)
```
```bash
# curl
curl -s -X POST "$BASE/v1/analyze/propagate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/photo.jpg",
       "identity_name": "Alex Rivera",
       "similarity_threshold": 0.85,
       "dry_run": false}'
```

### Update metadata

```python
# SDK
client.update_metadata("vec-12345", "Alex Rivera", relationship="colleague")
```
```bash
# curl
curl -s -X PATCH "$BASE/v1/metadata" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vector_id": "vec-12345",
       "name": "Alex Rivera",
       "relationship": "colleague"}'
```

---

## Note on `verification_ui.py`

The engine's integration includes a `verification_ui.py` browser-based search form. This component is not included in the SDK demo because it requires direct Qdrant client access — which is an internal engine service not available to SDK consumers. All search and filter functionality available through the public API is covered by `client.search()` and `client.search_vector()` in the scripts above.
