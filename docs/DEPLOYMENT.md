# CanopyAI Backend Deployment Guide

This guide details the complete production deployment procedure, secret management, monitoring, and rollback strategies for the **CanopyAI** FastAPI backend on **Render.com**.

---

## 1. Architecture & Infrastructure Overview

CanopyAI is deployed as a containerized Docker web service on Render:

- **Service Type**: Web Service (Docker)
- **Region**: Oregon, USA (`us-west` / `oregon`)
- **Port**: `8000`
- **Health Check Endpoint**: `/api/health`
- **Environment**: Python 3.11+ / Debian Slim
- **Container User**: Non-root `appuser` (UID 1000)
- **Reverse Proxy / SSL**: Managed automatically by Render (HTTPS enabled)

---

## 2. Infrastructure as Code (`render.yaml`)

The repository includes a declarative Render Blueprint configuration (`render.yaml`):

```yaml
services:
  - type: web
    name: canopyai-backend
    runtime: docker
    region: oregon
    plan: starter
    healthCheckPath: /api/health
    dockerfilePath: Dockerfile
    envVars:
      - key: PORT
        value: 8000
      - key: ENVIRONMENT
        value: production
      - key: MOCK_MODE
        value: "false"
      - key: LOG_LEVEL
        value: INFO
      - key: CORS_ORIGINS
        value: '["https://canopyai.vercel.app","http://localhost:3000","http://127.0.0.1:3000"]'
      - key: ANALYSIS_CACHE_TTL_SECONDS
        value: "3600"
      - key: LIST_CACHE_TTL_SECONDS
        value: "60"
      - key: GEE_SERVICE_ACCOUNT_KEY_FILE
        value: /etc/secrets/gee-key.json
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: SENTRY_DSN
        sync: false
    secretFiles:
      - name: gee-key
        mountPath: /etc/secrets/gee-key.json
```

---

## 3. Secrets Management

> [!CAUTION]
> **NEVER commit credential files, service account keys, or API tokens to version control.**

### 3.1 Google Earth Engine Service Account
1. In Google Cloud Console, create a Service Account with Earth Engine access enabled (`Earth Engine Resource Viewer` / `Earth Engine API User`).
2. Generate and download a JSON key file (`service-account-key.json`).
3. In the Render Dashboard:
   - Navigate to **Service Settings** -> **Secret Files**.
   - Add a Secret File named `gee-key` with Mount Path `/etc/secrets/gee-key.json`.
   - Paste the contents of your Google Service Account JSON key.
4. The backend reads this file via `GEE_SERVICE_ACCOUNT_KEY_FILE=/etc/secrets/gee-key.json`.

### 3.2 Supabase Database Credentials
Configure the following as **Environment Variables** in the Render Dashboard:
- `SUPABASE_URL`: e.g., `https://xyzproject.supabase.co`
- `SUPABASE_SERVICE_KEY`: Service role secret or secure backend API key.

### 3.3 Application Configuration Variables
| Variable | Production Value | Description |
|---|---|---|
| `PORT` | `8000` | Port uvicorn binds to inside the container |
| `ENVIRONMENT` | `production` | Enables production safeguards and structured JSON logging |
| `MOCK_MODE` | `false` | Set to `false` for real Earth Engine satellite data, `true` for mock fallback |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `["https://canopyai.vercel.app","http://localhost:3000"]` | Allowed browser origins |
| `ANALYSIS_CACHE_TTL_SECONDS` | `3600` | In-memory cache retention for individual analysis results |
| `LIST_CACHE_TTL_SECONDS` | `60` | In-memory cache retention for recent analysis listings |
| `SENTRY_DSN` | *(optional)* | Sentry DSN for production exception telemetry |

---

## 4. Step-by-Step Deployment Procedure

### Step 1: Connect Repository to Render
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Blueprint** (or **Web Service**).
3. Connect your GitHub repository (`CanopyAI` / `BIO-HACK`).
4. Select the `main` branch.

### Step 2: Configure Secrets & Environment
1. Under **Secret Files**, add `/etc/secrets/gee-key.json` and upload your Google Earth Engine service account key.
2. Under **Environment Variables**, provide your `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.
3. Verify that `MOCK_MODE` is set according to your needs (`false` for live satellite data, `true` for demo sandbox).

### Step 3: Trigger Build & Deployment
1. Click **Apply** or **Manual Deploy** -> **Deploy latest commit**.
2. Render will execute `docker build -t app:latest .` using the optimized multi-stage `Dockerfile`.
3. The build compiles dependencies, configures non-root user `appuser`, and boots Uvicorn on port `8000`.

### Step 4: Verification & Smoke Testing

Execute the following checks against your live Render service URL (e.g. `https://canopyai-backend.onrender.com`):

#### 1. Health & Dependency Status
```bash
curl -s https://canopyai-backend.onrender.com/api/health | jq .
```
Expected response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "production",
  "mock_mode": false,
  "uptime_seconds": 12.4,
  "services": {
    "earth_engine": "connected",
    "database": "connected"
  },
  "system": {
    "cpu_percent": 2.1,
    "memory_mb": 145.2,
    "memory_percent": 28.5
  }
}
```

#### 2. Interactive API Documentation
Open `https://canopyai-backend.onrender.com/docs` in your browser. Verify OpenAPI 3.1 schema and Swagger UI rendering.

#### 3. Run Pre-Flight Warm-Up Script
Run the automated warm-up verification locally against production:
```bash
python scripts/warm_up.py --url https://canopyai-backend.onrender.com
```

#### 4. Seed Demo History Data
Populate 10 global forest biome benchmark analyses for the live frontend:
```bash
python scripts/seed_demo_data.py --url https://canopyai-backend.onrender.com
```

---

## 5. Rollback & Disaster Recovery Procedures

If an unexpected failure or third-party outage occurs during production or live presentations, follow these tiered recovery procedures:

### Strategy 1: Instant Render Rollback (Zero Downtime)
1. Go to **Render Dashboard** -> **canopyai-backend** -> **Events**.
2. Locate the previous successful deployment.
3. Click the three dots `...` next to the deployment and click **Rollback to this deploy**.
4. Render immediately swaps container routing back to the proven build.

### Strategy 2: Emergency Mock Mode Failover (< 30 seconds)
If Earth Engine suffers a quota limit, rate limit, or upstream Google Cloud outage:
1. Go to **Render Dashboard** -> **canopyai-backend** -> **Environment**.
2. Change `MOCK_MODE` from `false` to `true`.
3. Click **Save Changes**.
4. The service restarts in ~10 seconds. All satellite analysis endpoints will now return statistically accurate, ecologically calibrated biome estimates instantly without external GEE calls.

### Strategy 3: Local Hot-Standby Tunnel (Emergency Presentation Fallback)
If cloud hosting is unreachable:
1. Start the backend locally:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. Expose via Cloudflare Tunnel or ngrok:
   ```bash
   ngrok http 8000
   ```
3. Update `NEXT_PUBLIC_API_URL` on the Vercel frontend or demo browser.

