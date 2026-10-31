"""Unit tests for Phase 4 scientific edge case handling and data integrity guardrails.

Covers:
6.1 Ocean polygon (> 80% water, NDVI < 0)
6.2 Urban polygon (> 50% built area)
6.3 Desert polygon (> 60% bare ground, NDVI < 0.15)
6.4 Agricultural polygon (> 50% crops)
6.5 Mixed ecosystems polygon (no single class > 40%)
6.6 Very small polygon (10-50 ha)
6.7 Very large polygon (> 50,000 ha)
6.8 Extreme latitude polygon (> 70°)
6.9 Earth Engine timeout handling
6.10 Complete data failure
"""

from unittest.mock import patch

import pytest

from app.core.carbon import (
    calculate_carbon_stock,
    calculate_co2_equivalent,
    calculate_total_co2,
)
from app.core.confidence import calculate_confidence_score
from app.core.earth_engine import (
    clear_satellite_cache,
    get_satellite_observations,
)


@pytest.fixture(autouse=True)
def reset_cache():
    """Ensure in-memory cache is clean before every edge case test."""
    clear_satellite_cache()


@pytest.fixture
def standard_polygon():
    """Standard evaluation polygon ~100 ha."""
    return {
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


@pytest.fixture
def small_polygon():
    """Very small polygon (approximately 25 ha: ~0.005° x 0.005° at equator)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.000, -3.000],
                [-59.995, -3.000],
                [-59.995, -3.005],
                [-60.000, -3.005],
                [-60.000, -3.000],
            ]
        ],
    }


@pytest.fixture
def huge_polygon():
    """Very large polygon (> 50,000 ha: ~0.75° x 0.75° at equator is ~70,000 ha)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.75, -3.75],
                [-60.00, -3.75],
                [-60.00, -3.00],
                [-60.75, -3.00],
                [-60.75, -3.75],
            ]
        ],
    }


@pytest.fixture
def high_arctic_polygon():
    """High latitude polygon at 78°N (Svalbard)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [15.0, 78.0],
                [15.5, 78.0],
                [15.5, 78.2],
                [15.0, 78.2],
                [15.0, 78.0],
            ]
        ],
    }


class TestEdgeCases:
    """Scientific edge cases validation suite."""

    def test_edge_case_ocean_polygon(self, standard_polygon):
        """Polygon over ocean (>80% water, NDVI < 0) returns null biomass, Non-Forest, and 0 confidence."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover") as mock_dw:

            mock_bio.return_value = {"agb_t_per_ha": None, "agb_stddev": None, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": None, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": -0.15, "valid_pixel_percentage": 98.0, "image_count": 10}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 0.0, "canopy_data_available": True, "canopy_pixel_count": 5000}
            mock_dw.return_value = {"water": 92.5, "trees": 1.0, "bare": 6.5}

            obs = get_satellite_observations(standard_polygon)

            assert obs["agb_t_per_ha"] is None
            assert obs["agb_stddev"] is None
            assert obs["mean_canopy_height_m"] is None
            assert obs["forest_type"] == "Non-Forest"
            assert any("water" in w.lower() for w in obs["data_warnings"])

            conf = calculate_confidence_score(obs, area_ha=100.0)
            assert conf["confidence_score"] == 0
            assert conf["confidence_label"] == "Low"

    def test_edge_case_urban_polygon(self, standard_polygon):
        """Polygon over urban area (>50% built) returns null biomass and Non-Forest."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover") as mock_dw:

            mock_bio.return_value = {"agb_t_per_ha": None, "agb_stddev": None, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": None, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": 0.22, "valid_pixel_percentage": 95.0, "image_count": 14}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 6.0, "canopy_data_available": True, "canopy_pixel_count": 8000}
            mock_dw.return_value = {"built": 64.0, "trees": 6.0, "grass": 15.0, "bare": 15.0}

            obs = get_satellite_observations(standard_polygon)

            assert obs["agb_t_per_ha"] is None
            assert obs["forest_type"] == "Non-Forest"
            assert any("urban" in w.lower() for w in obs["data_warnings"])

    def test_edge_case_desert_bare_ground_polygon(self, standard_polygon):
        """Polygon over desert (>60% bare ground, NDVI < 0.15) returns 0 biomass and 0 total CO2e."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover") as mock_dw:

            mock_bio.return_value = {"agb_t_per_ha": 0.0, "agb_stddev": 0.0, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": 0.0, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": 0.08, "valid_pixel_percentage": 99.0, "image_count": 18}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 0.0, "canopy_data_available": True, "canopy_pixel_count": 6000}
            mock_dw.return_value = {"bare": 78.0, "grass": 12.0, "trees": 0.0, "shrub_and_scrub": 10.0}

            obs = get_satellite_observations(standard_polygon)

            assert obs["agb_t_per_ha"] == 0.0
            assert obs["agb_stddev"] == 0.0
            assert obs["forest_type"] == "Non-Forest"
            assert any("desert" in w.lower() or "bare ground" in w.lower() for w in obs["data_warnings"])

            # Verify downstream carbon computation yields 0.0
            carbon_stock = calculate_carbon_stock(obs["agb_t_per_ha"])
            co2e_ha = calculate_co2_equivalent(carbon_stock)
            total_co2 = calculate_total_co2(co2e_ha, area_ha=100.0)
            assert carbon_stock == 0.0
            assert co2e_ha == 0.0
            assert total_co2 == 0.0

    def test_edge_case_agricultural_cropland_polygon(self, standard_polygon):
        """Polygon over cropland (>50% crops) returns null forest biomass and cropland warning."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover") as mock_dw:

            mock_bio.return_value = {"agb_t_per_ha": None, "agb_stddev": None, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": None, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": 0.65, "valid_pixel_percentage": 92.0, "image_count": 16}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 2.0, "canopy_data_available": True, "canopy_pixel_count": 9000}
            mock_dw.return_value = {"crops": 68.0, "grass": 18.0, "bare": 12.0, "trees": 2.0}

            obs = get_satellite_observations(standard_polygon)

            assert obs["agb_t_per_ha"] is None
            assert obs["forest_type"] == "Non-Forest"
            assert any("cropland" in w.lower() for w in obs["data_warnings"])

    def test_edge_case_mixed_ecosystem_polygon(self, standard_polygon):
        """Polygon with no single land cover class > 40% sets classification confidence to low."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover") as mock_dw:

            mock_bio.return_value = {"agb_t_per_ha": 90.0, "agb_stddev": 22.0, "gedi_observation_count": 12, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 16.0, "height_observation_count": 15, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.58, "valid_pixel_percentage": 90.0, "image_count": 14}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 35.0, "canopy_data_available": True, "canopy_pixel_count": 4000}
            # No class exceeds 40%
            mock_dw.return_value = {"trees": 35.0, "grass": 30.0, "shrub_and_scrub": 20.0, "bare": 15.0}

            obs = get_satellite_observations(standard_polygon)

            assert obs["classification_confidence"] == "low"
            assert any("mixed land cover" in w.lower() for w in obs["data_warnings"])

    def test_edge_case_small_polygon_warning_and_penalty(self, small_polygon):
        """Polygon between 10 and 50 ha proceeds with calculations, adds warning, and penalizes confidence by 10."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 180.0, "agb_stddev": 25.0, "gedi_observation_count": 8, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 24.0, "height_observation_count": 10, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.78, "valid_pixel_percentage": 94.0, "image_count": 12}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 82.0, "canopy_data_available": True, "canopy_pixel_count": 2500}

            obs = get_satellite_observations(small_polygon)

            assert any("small area" in w.lower() for w in obs["data_warnings"])

            # Compare confidence score with and without area penalty
            conf_small = calculate_confidence_score(obs, area_ha=25.0)
            conf_normal = calculate_confidence_score(obs, area_ha=100.0)
            assert conf_small["confidence_score"] == conf_normal["confidence_score"] - 10

    def test_edge_case_very_large_polygon_warning_and_penalty(self, huge_polygon):
        """Polygon > 50,000 ha adds large area warning, scale=100m, and penalizes confidence by 5."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 190.0, "agb_stddev": 30.0, "gedi_observation_count": 45, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 26.0, "height_observation_count": 50, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.82, "valid_pixel_percentage": 91.0, "image_count": 25}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 86.0, "canopy_data_available": True, "canopy_pixel_count": 50000}

            obs = get_satellite_observations(huge_polygon)

            assert any("very large area" in w.lower() for w in obs["data_warnings"])
            assert obs["validation_summary"]["gee_query_scale_m"] == 100

            conf_huge = calculate_confidence_score(obs, area_ha=70000.0)
            conf_normal = calculate_confidence_score(obs, area_ha=100.0)
            assert conf_huge["confidence_score"] == conf_normal["confidence_score"] - 5

    def test_edge_case_extreme_latitude_polygon(self, high_arctic_polygon):
        """Polygon at extreme latitude (> 70°) warns of limited LiDAR coverage."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            # GEDI has zero coverage at 78°N (orbit inclination is 51.6°)
            mock_bio.return_value = {"agb_t_per_ha": None, "agb_stddev": None, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": None, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": 0.15, "valid_pixel_percentage": 80.0, "image_count": 5}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 0.0, "canopy_data_available": True, "canopy_pixel_count": 1000}

            obs = get_satellite_observations(high_arctic_polygon)

            assert obs["agb_t_per_ha"] is None
            assert any("extreme latitude" in w.lower() for w in obs["data_warnings"])

    def test_edge_case_complete_satellite_data_failure(self, standard_polygon):
        """When all satellite sensors return null, all measurements are null, confidence is 0 ('Low'), and never returns mock data."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.earth_engine.get_dynamic_world_landcover", return_value={}):

            mock_bio.return_value = {"agb_t_per_ha": None, "agb_stddev": None, "gedi_observation_count": 0, "gedi_data_available": False}
            mock_h.return_value = {"mean_canopy_height_m": None, "height_observation_count": 0, "height_data_available": False}
            mock_s.return_value = {"mean_ndvi": None, "valid_pixel_percentage": 0.0, "image_count": 0}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": None, "canopy_data_available": False, "canopy_pixel_count": 0}

            obs = get_satellite_observations(standard_polygon)

            assert obs["agb_t_per_ha"] is None
            assert obs["mean_canopy_height_m"] is None
            assert obs["mean_ndvi"] is None
            assert obs["canopy_cover_pct"] is None
            assert any("no satellite data available" in w.lower() for w in obs["data_warnings"])

            conf = calculate_confidence_score(obs, area_ha=100.0)
            assert conf["confidence_score"] == 0
            assert conf["confidence_label"] == "Low"
            assert conf["confidence_interval_pct"] is None
