"""End-to-End tests for CanopyAI real satellite pipeline execution and scientific calculations."""

import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.schemas import AnalysisRequest, DataMode, GeoJSONPolygon
from app.services.analysis_service import AnalysisService

client = TestClient(app)

AMAZON_FOREST_POLYGON = {
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

OCEAN_POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [-30.05, 0.0],
            [-30.00, 0.0],
            [-30.00, -0.05],
            [-30.05, -0.05],
            [-30.05, 0.0],
        ]
    ],
}


class TestSatellitePipelineExecution:
    """Tests verifying the active satellite observation pipeline wired with Developer 1's modules."""

    def test_real_satellite_pipeline_with_mocked_gedi_observations(self):
        """Verify the full pipeline in real satellite mode with valid GEDI biomass observations."""
        custom_settings = Settings(
            mock_mode=False,
            gee_service_account_email="mock-sa@google.com",
            gee_private_key_path="fake_key.json",
            gee_project_id="mock-project",
        )
        service = AnalysisService(settings=custom_settings)

        # Mock satellite observation payload from earth_engine.py
        mock_satellite_obs = {
            "agb_t_per_ha": 250.0,
            "agb_stddev": 12.5,
            "gedi_observation_count": 45,
            "gedi_data_available": True,
            "mean_canopy_height_m": 26.8,
            "height_observation_count": 42,
            "height_data_available": True,
            "mean_ndvi": 0.82,
            "valid_pixel_percentage": 95.0,
            "image_count": 18,
            "ndvi_trend": [{"quarter": "2024-Q1", "ndvi": 0.81}, {"quarter": "2024-Q2", "ndvi": 0.83}],
            "data_sources": ["NASA GEDI Level 4A", "ESA Sentinel-2"],
        }

        with patch("app.core.earth_engine._ensure_initialized"):
            with patch("app.core.earth_engine.get_satellite_observations", return_value=mock_satellite_obs):
                req = AnalysisRequest(
                    polygon=GeoJSONPolygon(**AMAZON_FOREST_POLYGON),
                    analysis_type="detailed",
                )
                response = service.run_analysis(req)

                # Verify satellite data mode
                assert response.data_mode == DataMode.SATELLITE
                assert response.agb_t_per_ha == 250.0

                # Verify downstream scientific calculations
                # Tropical Moist Broadleaf root-to-shoot ratio = 0.21 -> BGB = 250 * 0.21 = 52.5
                assert response.bgb_t_per_ha is not None
                assert response.bgb_t_per_ha > 0
                assert response.total_biomass_t_per_ha == pytest.approx(response.agb_t_per_ha + response.bgb_t_per_ha, abs=0.01)

                # Carbon stock: total_biomass * 0.47
                expected_carbon = response.total_biomass_t_per_ha * 0.47
                assert response.carbon_t_per_ha == pytest.approx(expected_carbon, abs=0.01)

                # CO2e: carbon * (44/12)
                expected_co2e = response.carbon_t_per_ha * (44.0 / 12.0)
                assert response.co2e_t_per_ha == pytest.approx(expected_co2e, abs=0.01)

                # Total CO2: co2e_per_ha * area_ha
                assert response.total_co2e == pytest.approx(response.co2e_t_per_ha * response.area_ha, abs=0.5)

                # Confidence assessment
                assert response.confidence_score is not None
                assert response.confidence_score >= 0.70
                assert response.confidence_label in ["High", "Medium"]

    def test_satellite_data_null_biomass_handling(self):
        """Verify when GEDI observations are unavailable, downstream carbon fields return null with confidence 0."""
        custom_settings = Settings(
            mock_mode=False,
            gee_service_account_email="mock-sa@google.com",
            gee_private_key_path="fake_key.json",
            gee_project_id="mock-project",
        )
        service = AnalysisService(settings=custom_settings)

        # Mock observations returning None for biomass (e.g. persistent cloud cover or missing footprint)
        mock_null_obs = {
            "agb_t_per_ha": None,
            "agb_stddev": None,
            "gedi_observation_count": 0,
            "gedi_data_available": False,
            "mean_canopy_height_m": None,
            "height_observation_count": 0,
            "height_data_available": False,
            "mean_ndvi": 0.45,
            "valid_pixel_percentage": 20.0,
            "image_count": 4,
            "ndvi_trend": [],
            "data_sources": ["NASA GEDI Level 4A", "ESA Sentinel-2"],
        }

        with patch("app.core.earth_engine._ensure_initialized"):
            with patch("app.core.earth_engine.get_satellite_observations", return_value=mock_null_obs):
                req = AnalysisRequest(
                    polygon=GeoJSONPolygon(**AMAZON_FOREST_POLYGON),
                    analysis_type="quick",
                )
                response = service.run_analysis(req)

                assert response.data_mode == DataMode.SATELLITE
                assert response.agb_t_per_ha is None
                assert response.bgb_t_per_ha is None
                assert response.total_biomass_t_per_ha is None
                assert response.carbon_t_per_ha is None
                assert response.co2e_t_per_ha is None
                assert response.total_co2e is None
                assert response.confidence_score == 0.0
                assert response.confidence_label == "Low"
                assert any("No valid GEDI biomass observations" in w for w in response.data_warnings)

    def test_ocean_polygon_classification_and_biomass(self):
        """Verify analysis on open ocean/water polygon assigns Other/Non-Forest with zero or null biomass."""
        custom_settings = Settings(
            mock_mode=False,
            gee_service_account_email="mock-sa@google.com",
            gee_private_key_path="fake_key.json",
            gee_project_id="mock-project",
        )
        service = AnalysisService(settings=custom_settings)

        mock_ocean_obs = {
            "agb_t_per_ha": None,
            "agb_stddev": None,
            "gedi_observation_count": 0,
            "gedi_data_available": False,
            "mean_canopy_height_m": 0.0,
            "height_observation_count": 0,
            "height_data_available": False,
            "mean_ndvi": 0.0,
            "valid_pixel_percentage": 100.0,
            "image_count": 10,
            "ndvi_trend": [],
            "data_sources": ["NASA GEDI Level 4A", "ESA Sentinel-2"],
        }

        with patch("app.core.earth_engine._ensure_initialized"):
            with patch("app.core.earth_engine.get_satellite_observations", return_value=mock_ocean_obs):
                req = AnalysisRequest(
                    polygon=GeoJSONPolygon(**OCEAN_POLYGON),
                    analysis_type="quick",
                )
                response = service.run_analysis(req)
                assert response.data_mode == DataMode.SATELLITE
                assert response.agb_t_per_ha is None
                assert response.total_co2e is None


# Optional live Earth Engine test, executed only if real service account credentials are in environment
HAS_LIVE_EE_CREDS = bool(
    os.environ.get("GEE_SERVICE_ACCOUNT_EMAIL")
    and os.environ.get("GEE_PRIVATE_KEY_PATH")
    and os.environ.get("GEE_PROJECT_ID")
)


@pytest.mark.skipif(not HAS_LIVE_EE_CREDS, reason="Live GEE credentials not provided in environment")
def test_live_earth_engine_analysis():
    """Optional live integration test against actual Google Earth Engine API."""
    res = client.post(
        "/api/analyze",
        json={"polygon": AMAZON_FOREST_POLYGON, "analysis_type": "quick"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["data_mode"] == "satellite"
    assert data["agb_t_per_ha"] is not None
    assert 10.0 <= data["agb_t_per_ha"] <= 600.0

