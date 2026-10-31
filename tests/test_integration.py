"""End-to-end integration tests for CanopyAI complete analysis and reporting pipeline."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.schemas import GeoJSONPolygon
from app.services.analysis_service import AnalysisService, analysis_service
from app.services.database_service import DatabaseService
from app.services.mock_service import InMemoryAnalysisRepository

client = TestClient(app)

VALID_FOREST_POLYGON = {
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
}

INVALID_POLYGON_UNCLOSED = {
    "type": "Polygon",
    "coordinates": [
        [
            [-60.05, -3.12],
            [-60.00, -3.12],
            [-60.00, -3.16],
            [-60.05, -3.16],
            [-60.04, -3.11],
        ]
    ],
}

TINY_POLYGON = {
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
}


class TestMockModeE2EPipeline:
    """End-to-end verification of the full analysis, persistence, and reporting workflow in mock mode."""

    def test_full_mock_e2e_lifecycle(self):
        """Execute complete flow: POST -> GET by ID -> GET list -> GET report download."""
        # 1. POST /api/analyze with valid polygon
        payload = {
            "polygon": VALID_FOREST_POLYGON,
            "analysis_type": "detailed",
            "data_sources": ["sentinel-2", "gedi"],
        }
        post_res = client.post("/api/analyze", json=payload)
        assert post_res.status_code == 200, f"Analysis creation failed: {post_res.text}"
        data = post_res.json()

        # Verify all mandatory Phase 4 fields
        assert "analysis_id" in data
        analysis_id = data["analysis_id"]
        assert data["data_mode"] == "mock"
        assert data["area_ha"] > 10.0
        assert data["forest_type"] is not None
        assert data["ecoregion"] is not None
        assert data["canopy_cover_pct"] is not None
        assert data["canopy_data_available"] is True
        assert data["mean_canopy_height_m"] is not None
        assert data["agb_t_per_ha"] is not None
        assert data["bgb_t_per_ha"] is not None
        assert data["total_biomass_t_per_ha"] is not None
        assert data["carbon_fraction"] == 0.47
        assert data["carbon_t_per_ha"] is not None
        assert data["co2e_t_per_ha"] is not None
        assert data["total_co2e"] is not None
        assert 0.0 <= data["confidence_score"] <= 1.0
        assert data["confidence_label"] in ["High", "Moderate", "Medium", "Low"]
        assert isinstance(data["processing_time_seconds"], int)
        assert isinstance(data["data_warnings"], list)
        assert data["dominant_land_cover"] is not None
        assert data["classification_method"] is not None
        assert data["classification_confidence"] is not None
        assert data["recommended_standard"] is not None
        assert data["validation_summary"] is not None
        assert data["uncertainty"] is not None
        assert "disclaimer" in data

        # 2. GET /api/analyze/{id}
        get_res = client.get(f"/api/analyze/{analysis_id}")
        assert get_res.status_code == 200
        fetched = get_res.json()
        assert fetched["analysis_id"] == analysis_id
        assert fetched["area_ha"] == data["area_ha"]
        assert fetched["total_co2e"] == data["total_co2e"]

        # 3. GET /api/analyses (History)
        list_res = client.get("/api/analyses?limit=50&offset=0")
        assert list_res.status_code == 200
        history = list_res.json()
        assert history["total"] >= 1
        ids = [item["analysis_id"] for item in history.get("analyses", [])]
        assert analysis_id in ids

        # 4. GET /api/reports/{id}/download (PDF)
        pdf_res = client.get(f"/api/reports/{analysis_id}/download")
        assert pdf_res.status_code == 200
        assert pdf_res.headers.get("content-type") == "application/pdf"
        assert len(pdf_res.content) > 1000
        assert pdf_res.content[:4] == b"%PDF"

    def test_post_analyze_invalid_polygon_returns_422(self):
        """Verify invalid/unclosed polygon triggers 422 or 400 validation error."""
        payload = {
            "polygon": INVALID_POLYGON_UNCLOSED,
            "analysis_type": "quick",
        }
        res = client.post("/api/analyze", json=payload)
        assert res.status_code in [400, 422]
        data = res.json()
        assert data["error"] == "invalid_polygon"

    def test_post_analyze_too_small_polygon_returns_400(self):
        """Verify polygon smaller than 10 ha returns HTTP 400 polygon_too_small."""
        payload = {
            "polygon": TINY_POLYGON,
            "analysis_type": "quick",
        }
        res = client.post("/api/analyze", json=payload)
        assert res.status_code == 400
        data = res.json()
        assert data["error"] == "polygon_too_small"


class TestErrorScenariosAndFallbacks:
    """Verify system resiliency under network partitions, missing credentials, and timeouts."""

    def test_earth_engine_unavailable_fallback_to_mock(self):
        """Verify MOCK_MODE=False gracefully falls back to mock mode if GEE is uninitialized."""
        custom_settings = Settings(
            mock_mode=False,
            gee_service_account_email=None,
            gee_private_key_path=None,
            gee_project_id=None,
        )
        custom_service = AnalysisService(settings=custom_settings)

        # Patch _ensure_initialized to raise RuntimeError simulating missing credentials
        with patch("app.core.earth_engine._ensure_initialized", side_effect=RuntimeError("No credentials")):
            from app.models.schemas import AnalysisRequest, GeoJSONPolygon
            req = AnalysisRequest(
                polygon=GeoJSONPolygon(**VALID_FOREST_POLYGON),
                analysis_type="quick",
            )
            result = custom_service.run_analysis(req)

            assert result.data_mode == "mock"
            assert any("Satellite service unavailable" in w for w in result.data_warnings)

    def test_database_unavailable_returns_analysis_to_user(self):
        """Verify database write failure logs error and still returns analysis response."""
        mock_db = MagicMock()
        mock_db.save_analysis.side_effect = Exception("Supabase connection timeout")

        custom_service = AnalysisService(db_service=mock_db)
        from app.models.schemas import AnalysisRequest, GeoJSONPolygon
        req = AnalysisRequest(
            polygon=GeoJSONPolygon(**VALID_FOREST_POLYGON),
            analysis_type="quick",
        )

        # Should not raise exception; analysis is returned safely
        result = custom_service.run_analysis(req)
        assert result is not None
        assert result.area_ha > 0

    def test_analysis_endpoint_timeout_returns_504(self):
        """Verify POST /api/analyze returns HTTP 504 when processing exceeds timeout."""
        with patch("app.services.analysis_service.AnalysisService.run_analysis") as mock_run:
            # Simulate a slow analysis by sleeping longer than timeout
            import time

            def slow_run(*args, **kwargs):
                time.sleep(0.3)
                raise TimeoutError("Analysis timed out")

            mock_run.side_effect = slow_run

            from app.config import get_settings
            app.dependency_overrides[get_settings] = lambda: Settings(analysis_timeout_seconds=0.05)
            try:
                res = client.post(
                    "/api/analyze",
                    json={"polygon": VALID_FOREST_POLYGON, "analysis_type": "quick"},
                )
                assert res.status_code == 504
                assert res.json()["error"] == "analysis_timeout"
            finally:
                app.dependency_overrides.pop(get_settings, None)

    def test_report_endpoint_timeout_returns_504(self):
        """Verify GET /api/reports/{id}/download returns HTTP 504 when PDF generation times out."""
        # Seed an analysis first
        res = client.post(
            "/api/analyze",
            json={"polygon": VALID_FOREST_POLYGON, "analysis_type": "quick"},
        )
        analysis_id = res.json()["analysis_id"]

        with patch("app.api.reports.generate_pdf_report") as mock_pdf:
            import time

            def slow_pdf(*args, **kwargs):
                time.sleep(0.3)
                return b"fake"

            mock_pdf.side_effect = slow_pdf

            from app.config import get_settings
            app.dependency_overrides[get_settings] = lambda: Settings(pdf_timeout_seconds=0.05)
            try:
                report_res = client.get(f"/api/reports/{analysis_id}/download")
                assert report_res.status_code == 504
                assert report_res.json()["error"] == "report_timeout"
            finally:
                app.dependency_overrides.pop(get_settings, None)

    def test_health_check_endpoint_reports_status(self):
        """Verify GET /api/health includes mock_mode, earth_engine, and database status."""
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "mock_mode" in data
        assert data["earth_engine"] in ["connected", "disconnected", "mock"]
        assert data["database"] in ["connected", "disconnected"]
