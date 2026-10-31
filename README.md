# CanopyAI — Backend API Foundation

CanopyAI estimates forest biomass and carbon storage using satellite observation pipelines. This repository contains the backend REST API foundation developed by Developer 2.

---

## Architecture & Responsibilities

- **Developer 2 (Backend API Foundation)**:
  - FastAPI application structure, CORS, routing, and lifecycle (`app/main.py`, `app/config.py`).
  - Strict Pydantic v2 schemas and GeoJSON Polygon validation (`app/models/schemas.py`).
  - Mock simulation engine and in-memory persistence (`app/services/mock_service.py`).
  - Analysis workflow interface ready for Developer 1 (`app/services/analysis_service.py`).
  - PDF report generation service using ReportLab (`app/services/pdf_service.py`).
  - Supabase database service abstraction (`app/services/database_service.py`).
  - Centralized exception and error handling (`app/utils/errors.py`).
- **Developer 1 (Scientific & Satellite Pipeline)**:
  - Responsible for satellite data acquisition and Earth Engine integration (`app/core/*`).
  - Geo-processing algorithms and spatial metrics (`app/utils/geo.py`).

---

## Tech Stack

- **Python 3.11+** (Tested on Python 3.14)
- **FastAPI**
- **Uvicorn**
- **Pydantic v2 & Pydantic-Settings**
- **ReportLab**
- **Pytest**
- **Python-dotenv**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend operational status, version, server timestamp, and mock mode status |
| `POST` | `/api/analyze` | Submit GeoJSON Polygon and analysis configuration to compute biomass and carbon estimates (persisted to Supabase) |
| `GET` | `/api/analyze/{analysis_id}` | Retrieve previously computed analysis by unique ID from Supabase |
| `GET` | `/api/analyses` | Paginated list of analyses (`?limit=20&offset=0`) ordered by creation date, newest first |
| `GET` | `/api/reports/{analysis_id}/download` | Download summary PDF report for an analysis |
| `GET` | `/docs` | Interactive Swagger API documentation |
| `GET` | `/redoc` | Interactive ReDoc documentation |

---

## Phase 2: Supabase Persistence & Database Design

Analyses are persisted in PostgreSQL via Supabase in the `analyses` table:

```sql
CREATE TABLE IF NOT EXISTS public.analyses (
    analysis_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    polygon_geojson JSONB NOT NULL,
    area_ha DOUBLE PRECISION NOT NULL,
    forest_type TEXT,
    total_co2e DOUBLE PRECISION,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    data_mode TEXT NOT NULL CHECK (data_mode IN ('mock', 'satellite')),
    full_response JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'complete' CHECK (status IN ('complete', 'failed'))
);
```

### Mock Mode & Fallback Strategy
- **Without Supabase**: If `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` are unset, the service automatically runs in mock mode with an in-memory repository.
- **With Supabase**: When credentials are provided, analyses are persisted directly into Supabase and marked with `data_mode="mock"` (or `"satellite"` in production).
- Complete responses are preserved in `full_response` without field truncation.

---

## Data Contract Specifications

### Analysis Request (`POST /api/analyze`)

```json
{
  "polygon": {
    "type": "Polygon",
    "coordinates": [
      [
        [-60.05, -3.12],
        [-60.00, -3.12],
        [-60.00, -3.16],
        [-60.05, -3.16],
        [-60.05, -3.12]
      ]
    ]
  },
  "analysis_type": "quick",
  "data_sources": ["sentinel-2", "gedi"]
}
```

### Analysis Response Contract

- **Area Unit**: Hectares (`ha`)
- **Biomass Unit**: Tonnes per hectare (`t/ha`)
- **Carbon Unit**: Tonnes of carbon per hectare (`t/ha`)
- **CO2e Unit**: Tonnes of CO2 equivalent (`total_co2e`, `co2e_t_per_ha`)
- **Mode Flag**: `data_mode`: `"mock"` | `"satellite"`
- **Strict Compliance**: No carbon credit revenue projections or unverified claims.

---

## Local Development & Running

### 1. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 2. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Base: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Frontend Allowed Origin: `http://localhost:3000`

### 3. Run Test Suite

```bash
python -m pytest -v
```
