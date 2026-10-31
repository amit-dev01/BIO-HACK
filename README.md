# CanopyAI — Forest Biomass & Carbon Estimation Backend

CanopyAI estimates forest biomass and carbon storage using NASA GEDI Level 4A, ESA Sentinel-2 Harmonized, and Google Dynamic World satellite data. Results are screening-level estimates and do not constitute formal carbon credit verification.

---

## Architecture & Responsibilities

- **Developer 2 (Backend API, Integration & Deployment Engineer)**:
  - Complete REST API foundation, CORS, routing, and lifespan management (`app/main.py`, `app/config.py`).
  - Full analysis pipeline orchestration wiring Developer 1's scientific modules (`app/services/analysis_service.py`).
  - Strict Pydantic v2 data contracts, RFC 7946 GeoJSON validation, and schema definitions (`app/models/schemas.py`).
  - Mock simulation engine and in-memory persistence (`app/services/mock_service.py`).
  - Persistence layer with Supabase PostgreSQL and non-blocking in-memory fallback (`app/services/database_service.py`).
  - PDF report generation service using ReportLab & Matplotlib (`app/services/pdf_service.py`, `app/api/reports.py`).
  - Centralized exception and error handling pipeline (`app/utils/errors.py`).
  - Production Docker containerization, `docker-compose.yml`, and `render.yaml` one-click deployment.
  - End-to-end integration and timeout testing (`tests/test_integration.py`, `tests/test_e2e.py`).

- **Developer 1 (Scientific & Satellite Pipeline)**:
  - Google Earth Engine data acquisition and authentication (`app/core/earth_engine.py`).
  - NASA GEDI Level 4A Aboveground Biomass Density and Level 2A Canopy Height extraction.
  - ESA Sentinel-2 NDVI surface reflectance and 5-year quarterly vegetation trends.
  - Root-to-shoot biome-specific below-ground biomass algorithms (`app/core/biomass.py`).
  - Stoichiometric carbon stock and CO2 equivalent conversions (`app/core/carbon.py`).
  - Multi-factor forest biome and land-cover classification (`app/core/forest_classifier.py`).
  - Scientific confidence and empirical uncertainty assessment (`app/core/confidence.py`).
  - Geodesic spatial geometry calculations on WGS84 (`app/utils/geo.py`).

---

## Tech Stack

- **Python 3.11+**
- **FastAPI & Uvicorn**
- **Pydantic v2 & Pydantic-Settings**
- **Google Earth Engine API (`earthengine-api`)**
- **Supabase Python SDK & PostgreSQL**
- **ReportLab & Matplotlib**
- **Shapely & PyProj**
- **Docker & Docker Compose**
- **Pytest & HTTPX**

---

## Full Analysis Pipeline Workflow

```text
POST /api/analyze
  │
  ├─ 1. Validate Polygon Geometry (geo.validate_polygon)
  ├─ 2. Calculate Geodesic Area in Hectares (geo.calculate_area_ha)
  ├─ 3. Enforce Area Operational Limits (10 to 100,000 ha)
  │
  ├─ 4. Execution Mode Branch:
  │    ├─ IF MOCK_MODE or GEE Credentials Missing:
  │    │    └─ Simulate realistic biome biomass (mock_service.py)
  │    │         [Set data_mode="mock", add simulation warning if GEE failed]
  │    │
  │    └─ IF REAL SATELLITE MODE:
  │         ├─ Query Earth Engine Satellite Observations (60s timeout)
  │         │    - NASA GEDI L4A (AGBD t/ha)
  │         │    - NASA GEDI L2A (Canopy Height m)
  │         │    - Sentinel-2 NDVI & 5-year quarterly trend
  │         │    - Dynamic World canopy cover
  │         ├─ Classify Forest Biome & Ecoregion (forest_classifier.py)
  │         ├─ Calculate Below-Ground Biomass (biomass.py)
  │         ├─ Calculate Total Biomass Density (biomass.py)
  │         ├─ Calculate Carbon Stock Density (carbon.py)
  │         ├─ Calculate CO2 Equivalent Density (carbon.py)
  │         ├─ Calculate Total CO2 across Polygon Area (carbon.py)
  │         └─ Assess Scientific Confidence & Empirical Uncertainty (confidence.py)
  │
  ├─ 5. Assemble Structured Analysis Response
  ├─ 6. Persist to Supabase Database (10s timeout, non-blocking on failure)
  └─ 7. Return Response (Overall 120s timeout -> HTTP 504)
```

---

## Timeout Management

All timeouts are configurable via environment variables:

| Level | Config Setting | Default | Behavior on Expiry |
|---|---|---|---|
| **Earth Engine Queries** | `GEE_TIMEOUT_SECONDS` | `60s` | Sets satellite metrics to null, adds warning, continues with available data |
| **Analysis Request** | `ANALYSIS_TIMEOUT_SECONDS` | `120s` | Returns `HTTP 504 Gateway Timeout` with `{"error": "analysis_timeout"}` |
| **Database Operations** | `DATABASE_TIMEOUT_SECONDS` | `10s` | Logs error, non-blocking: analysis response still returned to user |
| **PDF Generation** | `PDF_TIMEOUT_SECONDS` | `30s` | Returns `HTTP 504 Gateway Timeout` with `{"error": "report_timeout"}` |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Diagnostic status: `mock_mode`, `earth_engine` (connected/disconnected/mock), `database` (connected/disconnected) |
| `POST` | `/api/analyze` | Submit GeoJSON Polygon and compute biomass & carbon estimates (120s timeout) |
| `GET` | `/api/analyze/{analysis_id}` | Retrieve previously computed analysis by unique ID |
| `GET` | `/api/analyses` | Paginated list of analyses (`?limit=20&offset=0`) ordered newest first |
| `GET` | `/api/reports/{analysis_id}/download` | Download comprehensive PDF report (30s timeout) |
| `GET` | `/docs` | Interactive OpenAPI Swagger documentation |
| `GET` | `/redoc` | Interactive ReDoc documentation |

---

## Deployment

### 1. Docker Production Image

The multi-stage `Dockerfile` uses `python:3.11-slim`, builds dependencies in an isolated stage, and outputs a minimal image (< 500MB) without development, test, or credential files:

```bash
docker build -t canopyai-backend .
docker run -p 8000:8000 -e MOCK_MODE=true canopyai-backend
```

### 2. Docker Compose (Local Development)

```bash
docker-compose up --build
```

### 3. One-Click Render Deployment

A production deployment blueprint is provided in `render.yaml`. Connect your repository to Render to deploy with Docker runtime:
- **Service Type**: Web Service
- **Runtime**: Docker
- **Environment Variables**:
  - `MOCK_MODE`: `false` (or `true` for staging)
  - `GEE_SERVICE_ACCOUNT_EMAIL`: Google Service Account email
  - `GEE_PRIVATE_KEY_PATH`: Path to secret service account key file
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_SERVICE_KEY`: Supabase service role key
  - `FRONTEND_URL`: Production Next.js frontend origin (e.g. `https://canopyai.vercel.app`)

---

## Running Tests

Run the complete test suite (194 tests covering unit, database, geospatial, PDF, and end-to-end integration):

```bash
python -m pytest -v
```
