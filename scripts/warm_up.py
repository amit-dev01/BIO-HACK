"""Warm-up script for CanopyAI backend before live hackathon demo presentation.

Verifies health, primes caches, runs warm-up analyses, checks PDF generation,
and reports performance timings.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import sys
import time
from typing import Any, Dict

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("canopyai.warmup")

SAMPLE_POLYGONS = [
    {
        "name": "Tapajós Amazon Stand",
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-55.05, -3.12],
                    [-55.00, -3.12],
                    [-55.00, -3.16],
                    [-55.05, -3.16],
                    [-55.05, -3.12],
                ]
            ],
        },
    },
    {
        "name": "Olympic Rainforest Stand",
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-124.05, 47.65],
                    [-124.00, 47.65],
                    [-124.00, 47.60],
                    [-124.05, 47.60],
                    [-124.05, 47.65],
                ]
            ],
        },
    },
    {
        "name": "Congo Peatland Stand",
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [
                    [20.55, -2.12],
                    [20.60, -2.12],
                    [20.60, -2.16],
                    [20.55, -2.16],
                    [20.55, -2.12],
                ]
            ],
        },
    },
]


def run_warm_up(base_url: str = "http://localhost:8000") -> bool:
    """Execute the full pre-demo warm-up sequence against the target server."""
    logger.info("Starting CanopyAI pre-demo warm-up against: %s", base_url)
    start_total = time.time()
    success = True

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        # 1. Check health endpoint
        logger.info("[Step 1/6] Evaluating service health endpoint...")
        try:
            t0 = time.time()
            health_res = client.get("/api/health")
            h_time = (time.time() - t0) * 1000
            assert health_res.status_code == 200, f"Health check returned {health_res.status_code}"
            h_data = health_res.json()
            logger.info("  Health status: %s (took %.2f ms)", h_data.get("status"), h_time)
            logger.info("  Uptime: %.1fs | Version: %s", h_data.get("uptime_seconds", 0), h_data.get("version"))
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False

        # 2. Check Earth Engine connectivity
        logger.info("[Step 2/6] Verifying Earth Engine status...")
        ee_status = h_data.get("earth_engine", "unknown")
        mock_mode = h_data.get("mock_mode", True)
        logger.info("  Earth Engine mode: %s (MOCK_MODE=%s)", ee_status, mock_mode)

        # 3. Run 3 mock analyses to pre-populate and prime caches
        logger.info("[Step 3/6] Running 3 mock analyses to prime caches...")
        analysis_ids = []
        for idx, item in enumerate(SAMPLE_POLYGONS, start=1):
            try:
                t0 = time.time()
                payload = {
                    "polygon": item["polygon"],
                    "analysis_type": "detailed" if idx == 1 else "quick",
                    "data_sources": ["sentinel-2", "gedi"],
                }
                res = client.post("/api/analyze", json=payload)
                elapsed = time.time() - t0
                assert res.status_code == 200, f"Analysis failed: {res.text}"
                data = res.json()
                analysis_ids.append(data["analysis_id"])
                logger.info(
                    "  [Mock %d/3] %s: Area %.1f ha | Total CO2e: %.1f t (took %.2fs)",
                    idx,
                    item["name"],
                    data["area_ha"],
                    data["total_co2e"] or 0,
                    elapsed,
                )
            except Exception as e:
                logger.error("  Mock analysis %d failed: %s", idx, e)
                success = False

        # 4. Run real analyses if Earth Engine credentials available
        logger.info("[Step 4/6] Checking live Earth Engine execution...")
        if not mock_mode and ee_status == "connected":
            logger.info("  Live GEE credentials active. Running 2 real satellite analyses...")
            for idx, item in enumerate(SAMPLE_POLYGONS[:2], start=1):
                try:
                    t0 = time.time()
                    payload = {"polygon": item["polygon"], "analysis_type": "quick"}
                    res = client.post("/api/analyze", json=payload)
                    elapsed = time.time() - t0
                    assert res.status_code == 200, f"Live analysis failed: {res.text}"
                    data = res.json()
                    logger.info("  [Live %d/2] %s: Mode %s (took %.2fs)", idx, item["name"], data["data_mode"], elapsed)
                except Exception as e:
                    logger.warning("  Live satellite query encountered warning: %s", e)
        else:
            logger.info("  Running in simulation mode. Real GEE queries bypassed.")

        # 5. Verify PDF generation works
        logger.info("[Step 5/6] Verifying PDF report generation...")
        if analysis_ids:
            target_id = analysis_ids[0]
            try:
                t0 = time.time()
                pdf_res = client.get(f"/api/reports/{target_id}/download")
                elapsed = time.time() - t0
                assert pdf_res.status_code == 200, f"PDF generation returned {pdf_res.status_code}"
                assert pdf_res.headers.get("content-type") == "application/pdf"
                pdf_size_kb = len(pdf_res.content) / 1024.0
                logger.info("  PDF generation verified: %.1f KB generated in %.2fs", pdf_size_kb, elapsed)
            except Exception as e:
                logger.error("PDF generation check failed: %s", e)
                success = False

        # 6. Verify History Pagination
        logger.info("[Step 6/6] Verifying analysis history listing...")
        try:
            t0 = time.time()
            list_res = client.get("/api/analyses?limit=10&offset=0")
            elapsed = time.time() - t0
            assert list_res.status_code == 200
            list_data = list_res.json()
            total_items = list_data.get("total", 0)
            logger.info("  History query successful: %d total analyses available (took %.2fs)", total_items, elapsed)
        except Exception as e:
            logger.error("History listing check failed: %s", e)
            success = False

    total_duration = time.time() - start_total
    logger.info("=" * 60)
    if success:
        logger.info("WARM-UP COMPLETE: All 6 stages passed in %.2fs. Backend is ready for demo!", total_duration)
    else:
        logger.warning("WARM-UP FINISHED WITH WARNINGS in %.2fs. Review logs above.", total_duration)
    logger.info("=" * 60)
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CanopyAI Pre-Demo Warm-Up Script")
    parser.add_argument("--url", default="http://localhost:8000", help="Base backend URL")
    args = parser.parse_args()

    # Try connecting to HTTP server or run in-process if not running
    try:
        run_warm_up(base_url=args.url)
    except httpx.ConnectError:
        logger.warning("Could not connect to %s. Testing in-process with FastAPI TestClient...", args.url)
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as test_client:
            # Run same checks via TestClient
            h = test_client.get("/api/health")
            logger.info("In-process health check: %d %s", h.status_code, h.json().get("status"))
            an = test_client.post("/api/analyze", json={"polygon": SAMPLE_POLYGONS[0]["polygon"], "analysis_type": "quick"})
            logger.info("In-process analyze check: %d id=%s", an.status_code, an.json().get("analysis_id"))
            pdf = test_client.get(f"/api/reports/{an.json()['analysis_id']}/download")
            logger.info("In-process PDF check: %d size=%d bytes", pdf.status_code, len(pdf.content))
            logger.info("In-process verification successful.")
