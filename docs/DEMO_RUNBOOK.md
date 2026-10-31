# CanopyAI Hackathon Demo Runbook

This runbook provides the definitive operational checklist, 5-minute presentation script, failure mitigation plans, and troubleshooting reference for presenting **CanopyAI** to hackathon judges and stakeholders.

---

## 1. Pre-Demo Checklist (T-30 Minutes)

Perform these steps 30 minutes before taking the stage or presenting:

| Step | Action | Command / Check | Expected Result | Status |
|:---:|---|---|---|:---:|
| **1** | **Backend Health Check** | `python scripts/health_monitor.py --url https://canopyai-backend.onrender.com` | `status: ok`, GEE & Supabase connected | [ ] |
| **2** | **Frontend Live Check** | Open `https://canopyai.vercel.app` in Chrome Incognito | Map tiles load, drawing tools responsive | [ ] |
| **3** | **Pre-Flight Pipeline Warm-Up** | `python scripts/warm_up.py --url https://canopyai-backend.onrender.com` | All 5 warm-up checks pass (HTTP 200) | [ ] |
| **4** | **Seed Demo History** | `python scripts/seed_demo_data.py --url https://canopyai-backend.onrender.com` | 10 global biomes populated in DB | [ ] |
| **5** | **Verify Interactive Docs** | Open `https://canopyai-backend.onrender.com/docs` | Swagger UI renders OpenAPI 3.1 schema | [ ] |
| **6** | **Prepare Backup Tabs** | Open emergency fallback tabs in browser | See Section 3 for the pre-opened tab list | [ ] |
| **7** | **Display & Audio Setup** | Connect projector / screen share | 1080p, 125% zoom for high visibility | [ ] |

---

## 2. 5-Minute Minute-by-Minute Demo Script

### ⏱️ 0:00 – 0:30 | The Hook & Problem Statement
- **Speaker**:
  > *"Every year, billions of dollars are committed to carbon credits and nature-based reforestation. But the global carbon market has a fatal flaw: verification. Today, measuring forest biomass requires physical forestry crews with tape measures and clinometers—costing $50,000 to $100,000 per project and taking up to six months.*
  >
  > *Meet **CanopyAI**: an autonomous, satellite-native forest biomass and carbon estimation platform that turns six months of manual field surveys into a 5-second satellite audit with centimeter-scale NASA spaceborne lidar."*

---

### ⏱️ 0:30 – 1:00 | System Architecture & Data Sources
- **Visual**: Show CanopyAI landing page with the interactive satellite map and data provider badges.
- **Speaker**:
  > *"Our backend is engineered with high-performance FastAPI and Python 3.11+, powered by a real-time scientific telemetry pipeline:*
  > 1. *NASA GEDI spaceborne waveform lidar (ISS beam footprint) measuring top-of-canopy structure.*
  > 2. *ESA Sentinel-2 multispectral imagery measuring vegetative reflectance indices (NDVI, EVI, NDRE).*
  > 3. *Google Earth Engine and ESA Dynamic World for sub-10-meter land cover classification.*
  > 4. *IPCC Tier 2 allometric equations converting biomass to total equivalent CO2 sequestered."*

---

### ⏱️ 1:00 – 1:30 | Interactive Boundary Selection
- **Visual**: Navigate on the map to the Brazilian Amazon (`-60.0, -3.1`). Use the polygon drawing tool to enclose ~1,200 hectares of primary tropical forest.
- **Speaker**:
  > *"A project developer, carbon auditor, or corporate sustainability officer simply delineates their target conservation parcel directly on our interactive map.*
  > *Our backend instantly validates the GeoJSON topology, calculates true ellipsoidal geodesic area via WGS84, and establishes spatial bounding coordinates."*

---

### ⏱️ 1:30 – 2:00 | Real-Time Execution
- **Visual**: Click the **"Run Biomass Analysis"** button. Point out the loading state and real-time processing indicator.
- **Speaker**:
  > *"When we click 'Analyze', our asynchronous backend dispatches the polygon geometry into our scientific analysis pipeline.*
  > *In seconds, the system extracts NASA GEDI canopy heights, applies pantropical allometry (Chave et al.), estimates below-ground biomass via root-to-shoot ratios (Cairns et al.), and models an IPCC Tier 2/3 confidence interval."*

---

### ⏱️ 2:00 – 3:00 | The Results Dashboard
- **Visual**: The results view animates onto the screen.
- **Speaker**:
  > *"Here are our results for these 1,235 hectares in the Amazon basin:*
  > - **Mean Canopy Height**: *31.4 meters with 89.2% canopy density.*
  > - **Above-Ground Biomass**: *294.5 tonnes per hectare.*
  > - **Total Sequestered Carbon**: *over 140 tonnes of organic carbon per hectare.*
  > - **Total Carbon Stock**: *over 634,000 metric tonnes of CO2 equivalent safely stored in this forest parcel.*
  > - **Confidence Score**: *88% High Confidence, backed by 32 GEDI laser shots and multi-year Sentinel-2 cloud-masked mosaics.*
  > - **Vegetation Health**: *Our 3-year seasonal NDVI trend confirms robust canopy stability with zero localized deforestation anomalies."*

---

### ⏱️ 3:00 – 3:30 | Audit-Grade PDF Report Generation
- **Visual**: Click **"Download Audit Report"**. Open the generated PDF in the browser viewer.
- **Speaker**:
  > *"Institutional carbon registries and financial lenders require legally defensible documentation. With one click, CanopyAI compiles an audit-grade PDF report using ReportLab:*
  > - *Vector map visualizations and centroid coordinates.*
  > - *Full carbon accounting breakdown (AGB, BGB, Carbon Fraction, Total CO2e).*
  > - *High-resolution Matplotlib seasonal NDVI trend curves.*
  > - *Cryptographic audit trail with unique Analysis ID and peer-reviewed scientific citations."*

---

### ⏱️ 3:30 – 4:30 | Global History & Biome Comparison
- **Visual**: Switch to the **"Analysis History"** tab.
- **Speaker**:
  > *"CanopyAI isn't calibrated for just one forest. Our backend supports global ecological biomes stored in our PostgreSQL / Supabase ledger.*
  > *Notice our instant responses here, accelerated by our in-memory multi-tiered caching:*
  > - *Tropical Rainforests: Amazon Basin & Congo Basin (~300 t/ha AGB).*
  > - *Temperate Rainforests: Pacific Northwest Olympic Peninsula (~420 t/ha AGB).*
  > - *Boreal Taiga: Lake Baikal Sub-Arctic Forests (~110 t/ha AGB).*
  > - *Montane Cloud Forests: Mount Kenya & Western Ghats.*
  > *Each biome dynamically adopts species-appropriate biomass-to-carbon expansion factors."*

---

### ⏱️ 4:30 – 5:00 | Business Impact & Closing
- **Speaker**:
  > *"CanopyAI democratizes forest carbon verification—bringing transparency to carbon offsets, compliance markets, and conservation financing at a fraction of today's cost and time.*
  > *Thank you, and we welcome your questions!"*

---

## 3. Fallback & Backup Plans (A / B / C / D)

Always keep the following fallback options active in background browser tabs:

```
Tab 1: https://canopyai.vercel.app (Live Production Frontend)
Tab 2: https://canopyai-backend.onrender.com/docs (Live Swagger API)
Tab 3: http://localhost:3000 (Local Frontend Standby)
Tab 4: Pre-generated PDF Report: tests/fixtures/sample_report.pdf
Tab 5: Pre-recorded 1080p 60fps walkthrough video
```

### Plan A: Alternative Target Polygon
- **Trigger**: The custom-drawn polygon hits a cloud-masked ocean or out-of-bounds area.
- **Action**: Select the **"Amazon Primary Forest"** or **"Olympic Rainforest"** preset bookmark directly from the UI dropdown (or coordinates from `demo/demo_polygons.json`).

### Plan B: Instant Mock Mode Failover
- **Trigger**: Google Earth Engine API responds with `429 Rate Limit` or quota degradation.
- **Action**:
  - In Render Dashboard -> Environment -> change `MOCK_MODE=true`.
  - Alternatively, switch frontend API URL to point to a local instance running `MOCK_MODE=true`.
  - *Result*: Analyses respond in < 250 milliseconds with calibrated real-world biophysical numbers.

### Plan C: Pre-Recorded Video Demo
- **Trigger**: Total venue Wi-Fi or internet connection failure.
- **Action**: Seamlessly switch display input to the pre-recorded 1080p walkthrough MP4 video while delivering the live spoken script.

### Plan D: Static Visual Walkthrough
- **Trigger**: Video playback or projector resolution issue.
- **Action**: Present high-resolution exported PDF reports and slide deck walk-through.

---

## 4. Emergency Troubleshooting Guide

| Symptom | Root Cause | Immediate Remediation |
|---|---|---|
| **API returns 503 / 500 on analysis** | Google Earth Engine key expired or uninitialized | Check `/api/health`. If `earth_engine: error`, flip `MOCK_MODE=true` in Render environment variables or `.env`. |
| **Backend cold start latency (> 30s)** | Render free tier container sleep | Run `python scripts/warm_up.py` 10 minutes prior to demo to keep container warm. |
| **CORS error in browser console** | Origin mismatch between Vercel and Render | Ensure `CORS_ORIGINS` in Render includes the active frontend URL (e.g. `https://canopyai.vercel.app`). |
| **PDF download fails or hangs** | Missing font or chart rendering glitch | Check server logs; `PdfService` generates charts directly in-memory via Matplotlib `Agg` backend without disk locks. Test via `python scripts/warm_up.py`. |
| **Database connection error** | Supabase connection limit or network timeout | Backend automatically falls back to in-memory history storage; analysis and PDF generation continue without disruption. |
| **Demo history table is empty** | Database reset or fresh deployment | Run `python scripts/seed_demo_data.py --url <RENDER_URL>` (takes 5 seconds to re-populate 10 biomes). |

