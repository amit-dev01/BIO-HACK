"""Frontend-Backend Integration Tests for CanopyAI.

Validates exact Next.js frontend contract expectations:
- CORS preflight and allowed origins
- Exact request payload formats
- Strict snake_case field definitions and precision
- Standardized error envelopes with request IDs
- Concurrent load tolerance under parallel requests
"""

import concurrent.futures
import re
import time
from typing import Any, Dict, List
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FRONTEND_EXACT_PAYLOAD = {
    "polygon": {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.05, -3.12],
                [-60.00, -3.12],
                [-60.00, -3.16],
                [-60.05, -3.16],
                [-60.05, -3.12],
            ]
        ],
    },
    "analysis_type": "quick",
    "data_sources": ["sentinel-2", "gedi", "dynamic_world"],
}


class TestFrontendContractIntegration:
    """Verifies that the backend contract matches the Next.js frontend requirements."""

    def test_cors_preflight_and_headers(self):
        """Verify CORS OPTIONS preflight response and headers for frontend origins."""
        # Test OPTIONS preflight for Next.js frontend
        headers = {
            "Origin": "https://canopyai.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        res = client.options("/api/analyze", headers=headers)
        assert res.status_code == 200
        assert res.headers.get("access-control-allow-origin") == "https://canopyai.vercel.app"
        assert "POST" in res.headers.get("access-control-allow-methods", "")
        assert "content-type" in res.headers.get("access-control-allow-headers", "").lower()

        # Also verify local development origin
        local_headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        local_res = client.options("/api/analyze", headers=local_headers)
        assert local_res.status_code == 200
        assert local_res.headers.get("access-control-allow-origin") == "http://localhost:3000"

        # Also verify dynamic Vercel preview domains
        preview_headers = {
            "Origin": "https://bio-hack-dpl-4bup1ajgg.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        preview_res = client.options("/api/analyze", headers=preview_headers)
        assert preview_res.status_code == 200
        assert preview_res.headers.get("access-control-allow-origin") == "https://bio-hack-dpl-4bup1ajgg.vercel.app"

    def test_exact_frontend_request_format(self):
        """Verify that sending the exact frontend payload structure returns 200 and expected schema."""
        res = client.post("/api/analyze", json=FRONTEND_EXACT_PAYLOAD)
        assert res.status_code == 200
        data = res.json()

        # Verify X-Request-ID response header
        assert "X-Request-ID" in res.headers
        assert res.headers["X-Request-ID"].startswith("req_")

        # Verify essential frontend UI fields
        expected_keys = [
            "analysis_id",
            "timestamp",
            "polygon",
            "area_ha",
            "forest_type",
            "ecoregion",
            "canopy_cover_pct",
            "canopy_data_available",
            "mean_canopy_height_m",
            "agb_t_per_ha",
            "bgb_t_per_ha",
            "total_biomass_t_per_ha",
            "carbon_fraction",
            "carbon_t_per_ha",
            "co2e_t_per_ha",
            "total_co2e",
            "confidence_score",
            "confidence_label",
            "confidence_interval_pct",
            "ndvi_trend",
            "data_sources",
            "processing_time_seconds",
            "data_mode",
            "dominant_land_cover",
            "classification_method",
            "classification_confidence",
            "recommended_standard",
            "data_warnings",
            "validation_summary",
            "uncertainty",
            "disclaimer",
        ]
        for key in expected_keys:
            assert key in data, f"Missing expected frontend key: {key}"

    def test_field_compatibility_and_snake_case(self):
        """Verify all keys are strictly snake_case, correctly typed, and have appropriate precision."""
        res = client.post("/api/analyze", json=FRONTEND_EXACT_PAYLOAD)
        assert res.status_code == 200
        data = res.json()

        snake_case_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for key, value in data.items():
            assert snake_case_pattern.match(key), f"Field '{key}' is not strictly snake_case"

        # Verify numeric types
        assert isinstance(data["area_ha"], (int, float))
        assert isinstance(data["agb_t_per_ha"], (int, float))
        assert isinstance(data["processing_time_seconds"], int)
        assert isinstance(data["data_warnings"], list)
        assert isinstance(data["data_sources"], list)
        assert data["data_mode"] in ["mock", "satellite"]

        # Ensure no carbon credit revenue claims
        assert not any("revenue" in k.lower() or "price" in k.lower() for k in data.keys())

    def test_error_response_format_and_request_id(self):
        """Verify error envelopes match the frontend's {error, message, request_id} contract."""
        # 1. Invalid Polygon
        bad_payload = {
            "polygon": {
                "type": "Polygon",
                "coordinates": [[[-60.0, -3.0], [-60.0, -3.1], [-60.1, -3.1]]],  # Unclosed, <4 points
            },
            "analysis_type": "quick",
        }
        res_422 = client.post("/api/analyze", json=bad_payload)
        assert res_422.status_code in [400, 422]
        err_422 = res_422.json()
        assert "error" in err_422
        assert "message" in err_422
        assert "request_id" in err_422
        assert err_422["request_id"].startswith("req_")

        # 2. Polygon Too Small (< minimum threshold)
        small_payload = {
            "polygon": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-60.00005, -3.12005],
                        [-60.00000, -3.12005],
                        [-60.00000, -3.12000],
                        [-60.00005, -3.12000],
                        [-60.00005, -3.12005],
                    ]
                ],
            },
            "analysis_type": "quick",
        }
        res_400 = client.post("/api/analyze", json=small_payload)
        assert res_400.status_code == 400
        err_400 = res_400.json()
        assert err_400["error"] == "polygon_too_small"
        assert "message" in err_400
        assert "request_id" in err_400

        # 3. Missing Analysis 404
        res_404 = client.get("/api/analyze/missing-analysis-999")
        assert res_404.status_code == 404
        err_404 = res_404.json()
        assert err_404["error"] == "analysis_not_found"
        assert "request_id" in err_404

    def test_concurrent_analysis_load(self):
        """Simulate 10 parallel analysis requests from concurrent frontend users."""
        start_ts = time.time()
        num_requests = 10

        def send_request(idx: int) -> Dict[str, Any]:
            # Slightly vary longitude to ensure independent footprints
            lon_offset = idx * 0.001
            payload = {
                "polygon": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-60.05 + lon_offset, -3.12],
                            [-60.00 + lon_offset, -3.12],
                            [-60.00 + lon_offset, -3.16],
                            [-60.05 + lon_offset, -3.16],
                            [-60.05 + lon_offset, -3.12],
                        ]
                    ],
                },
                "analysis_type": "quick",
                "data_sources": ["sentinel-2", "gedi"],
            }
            res = client.post("/api/analyze", json=payload)
            return {"status_code": res.status_code, "data": res.json()}

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(send_request, i) for i in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_elapsed = time.time() - start_ts

        # Verify all completed successfully with 200 OK
        assert len(results) == num_requests
        for r in results:
            assert r["status_code"] == 200
            assert "analysis_id" in r["data"]
            assert r["data"]["area_ha"] > 10.0

        # Average latency per request should be fast (< 2.0s per request under parallel load)
        assert total_elapsed < 10.0, f"10 concurrent requests took {total_elapsed:.2f}s (target < 10s)"
