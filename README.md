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
| `POST` | `/api/analyze` | Submit GeoJSON Polygon and analysis configuration to compute biomass and carbon estimates |
| `GET` | `/api/analyze/{analysis_id}` | Retrieve previously computed analysis by unique ID |
| `GET` | `/api/analyses` | Paginated list of session analyses (`?page=1&limit=10`) |
| `GET` | `/api/reports/{analysis_id}/download` | Download summary PDF report for an analysis |
| `GET` | `/docs` | Interactive Swagger API documentation |
| `GET` | `/redoc` | Interactive ReDoc documentation |

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
