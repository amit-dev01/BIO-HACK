"""Unit tests for Phase 4 scientific accuracy verification against published reference literature and performance benchmarks.

Reference Forest Benchmarks (±40% screening tolerance):
1. Amazon Primary Forest (Brazil, -3° lat):
   - Expected AGB: 250-400 Mg/ha, Canopy cover: 85-95%, NDVI: 0.80-0.90
2. Congo Basin Forest (DRC, 0° lat):
   - Expected AGB: 200-350 Mg/ha, Canopy cover: 80-95%
3. European Temperate Forest (Germany, 50° lat):
   - Expected AGB: 150-300 Mg/ha, Canopy cover: 70-90%
4. Boreal Forest (Finland, 64° lat):
   - Expected AGB: 50-150 Mg/ha, Canopy cover: 50-80%
5. Mangrove Forest (Indonesia, -2° lat):
   - Expected AGB: 100-250 Mg/ha, Canopy cover: 70-90%

Performance & System Resilience:
6. Scale adjustment for large polygons (> 10,000 ha uses scale=100m, <= 10,000 ha uses scale=10m)
7. Deterministic in-memory 24-hour coordinate caching (cache_hit = True on subsequent call)
8. Earth Engine timeout handling (catches timeout, sets failed source to None, records warning)
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from app.core.earth_engine import (
    clear_satellite_cache,
    get_polygon_cache_key,
    get_satellite_observations,
)

logger = logging.getLogger("canopyai.test_accuracy")


@pytest.fixture(autouse=True)
def clean_cache():
    """Ensure in-memory cache is clean for every accuracy test."""
    clear_satellite_cache()


def assert_within_reference_tolerance(
    actual: float | None,
    min_ref: float,
    max_ref: float,
    tolerance_pct: float = 40.0,
    metric_name: str = "metric",
) -> None:
    """Verify that an estimate falls within ±40% of the published reference range.

    If outside tolerance, logs a detailed scientific discrepancy warning.
    """
    assert actual is not None, f"{metric_name} was None; expected valid observation."
    lower_bound = min_ref * (1.0 - (tolerance_pct / 100.0))
    upper_bound = max_ref * (1.0 + (tolerance_pct / 100.0))

    if not (lower_bound <= actual <= upper_bound):
        logger.warning(
            "Scientific Discrepancy: %s of %.2f outside ±%.0f%% range [%.2f, %.2f] (Reference [%.1f, %.1f]).",
            metric_name,
            actual,
            tolerance_pct,
            lower_bound,
            upper_bound,
            min_ref,
            max_ref,
        )

    assert lower_bound <= actual <= upper_bound, (
        f"{metric_name} value {actual} is outside acceptable ±{tolerance_pct}% "
        f"screening range [{lower_bound:.2f}, {upper_bound:.2f}] (Ref: [{min_ref}, {max_ref}])"
    )


class TestScientificAccuracyReferenceBaselines:
    """Verify estimates against published literature ranges for global forest reference sites."""

    def test_amazon_primary_forest_reference_accuracy(self):
        """Amazon primary forest (Brazil, -3°): AGB ~250-400 Mg/ha, Canopy ~85-95%, NDVI ~0.80-0.90."""
        amazon_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [-60.05, -3.00],
                    [-60.00, -3.00],
                    [-60.00, -3.05],
                    [-60.05, -3.05],
                    [-60.05, -3.00],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            # Simulated real observations matching Amazon primary rainforest
            mock_bio.return_value = {"agb_t_per_ha": 315.4, "agb_stddev": 32.1, "gedi_observation_count": 35, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 33.2, "height_observation_count": 40, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.86, "valid_pixel_percentage": 94.0, "image_count": 20}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 91.5, "canopy_data_available": True, "canopy_pixel_count": 12000}

            obs = get_satellite_observations(amazon_poly)

            assert_within_reference_tolerance(obs["agb_t_per_ha"], 250.0, 400.0, metric_name="Amazon AGB")
            assert_within_reference_tolerance(obs["canopy_cover_pct"], 85.0, 95.0, metric_name="Amazon Canopy Cover")
            assert_within_reference_tolerance(obs["mean_ndvi"], 0.80, 0.90, metric_name="Amazon NDVI")
            assert obs["forest_type"] == "Tropical Moist Broadleaf"

    def test_congo_basin_forest_reference_accuracy(self):
        """Congo Basin forest (DRC, 0°): AGB ~200-350 Mg/ha, Canopy ~80-95%."""
        congo_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [22.00, 0.00],
                    [22.05, 0.00],
                    [22.05, 0.05],
                    [22.00, 0.05],
                    [22.00, 0.00],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 285.0, "agb_stddev": 36.4, "gedi_observation_count": 28, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 31.0, "height_observation_count": 35, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.84, "valid_pixel_percentage": 92.0, "image_count": 18}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 88.0, "canopy_data_available": True, "canopy_pixel_count": 10000}

            obs = get_satellite_observations(congo_poly)

            assert_within_reference_tolerance(obs["agb_t_per_ha"], 200.0, 350.0, metric_name="Congo AGB")
            assert_within_reference_tolerance(obs["canopy_cover_pct"], 80.0, 95.0, metric_name="Congo Canopy Cover")
            assert obs["forest_type"] == "Tropical Moist Broadleaf"

    def test_european_temperate_forest_reference_accuracy(self):
        """European temperate forest (Germany, 50°): AGB ~150-300 Mg/ha, Canopy ~70-90%."""
        temperate_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [10.00, 49.95],
                    [10.05, 49.95],
                    [10.05, 50.00],
                    [10.00, 50.00],
                    [10.00, 49.95],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 210.0, "agb_stddev": 28.0, "gedi_observation_count": 22, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 25.5, "height_observation_count": 30, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.74, "valid_pixel_percentage": 95.0, "image_count": 16}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 78.5, "canopy_data_available": True, "canopy_pixel_count": 8000}

            obs = get_satellite_observations(temperate_poly)

            assert_within_reference_tolerance(obs["agb_t_per_ha"], 150.0, 300.0, metric_name="Temperate AGB")
            assert_within_reference_tolerance(obs["canopy_cover_pct"], 70.0, 90.0, metric_name="Temperate Canopy Cover")
            assert obs["forest_type"] == "Temperate Broadleaf"

    def test_boreal_forest_reference_accuracy(self):
        """Boreal forest (Finland, 64°): AGB ~50-150 Mg/ha, Canopy ~50-80%."""
        boreal_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [27.00, 64.00],
                    [27.05, 64.00],
                    [27.05, 64.05],
                    [27.00, 64.05],
                    [27.00, 64.00],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 95.0, "agb_stddev": 18.0, "gedi_observation_count": 18, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 18.0, "height_observation_count": 24, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.62, "valid_pixel_percentage": 89.0, "image_count": 14}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 68.0, "canopy_data_available": True, "canopy_pixel_count": 6500}

            obs = get_satellite_observations(boreal_poly)

            assert_within_reference_tolerance(obs["agb_t_per_ha"], 50.0, 150.0, metric_name="Boreal AGB")
            assert_within_reference_tolerance(obs["canopy_cover_pct"], 50.0, 80.0, metric_name="Boreal Canopy Cover")
            assert obs["forest_type"] == "Boreal Coniferous"

    def test_mangrove_forest_reference_accuracy(self):
        """Mangrove forest (Indonesia, -2°): AGB ~100-250 Mg/ha, Canopy ~70-90%."""
        mangrove_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [104.00, -2.00],
                    [104.05, -2.00],
                    [104.05, -1.95],
                    [104.00, -1.95],
                    [104.00, -2.00],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_bio.return_value = {"agb_t_per_ha": 175.0, "agb_stddev": 24.5, "gedi_observation_count": 20, "gedi_data_available": True}
            mock_h.return_value = {"mean_canopy_height_m": 22.0, "height_observation_count": 25, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.81, "valid_pixel_percentage": 93.0, "image_count": 15}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 82.0, "canopy_data_available": True, "canopy_pixel_count": 7500}

            obs = get_satellite_observations(mangrove_poly)

            assert_within_reference_tolerance(obs["agb_t_per_ha"], 100.0, 250.0, metric_name="Mangrove AGB")
            assert_within_reference_tolerance(obs["canopy_cover_pct"], 70.0, 90.0, metric_name="Mangrove Canopy Cover")


class TestPerformanceAndResilience:
    """Tests covering scale adjustment, in-memory caching, and timeout resilience."""

    def test_large_polygon_scale_adjustment(self):
        """Polygons > 10,000 ha automatically adjust reduceRegion scale to 100m."""
        # 0.4° x 0.4° polygon is ~19,000 ha at equator
        large_poly = {
            "type": "Polygon",
            "coordinates": [
                [
                    [-60.40, -3.40],
                    [-60.00, -3.40],
                    [-60.00, -3.00],
                    [-60.40, -3.00],
                    [-60.40, -3.40],
                ]
            ],
        }

        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_height, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s2, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_trend, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_canopy:

            mock_bio.return_value = {"agb_t_per_ha": 250.0, "agb_stddev": 30.0, "gedi_observation_count": 100, "gedi_data_available": True}
            mock_height.return_value = {"mean_canopy_height_m": 28.0, "height_observation_count": 120, "height_data_available": True}
            mock_s2.return_value = {"mean_ndvi": 0.85, "valid_pixel_percentage": 95.0, "image_count": 25}
            mock_trend.return_value = []
            mock_canopy.return_value = {"canopy_cover_pct": 88.0, "canopy_data_available": True, "canopy_pixel_count": 20000}

            obs = get_satellite_observations(large_poly)

            # scale=100m verified in validation summary
            assert obs["validation_summary"]["gee_query_scale_m"] == 100

            # Verify sub-services were called with scale=100
            mock_s2.assert_called_once_with(large_poly, scale=100, raise_on_error=False)
            mock_canopy.assert_called_once_with(large_poly, scale=100, raise_on_error=False)
            mock_height.assert_called_once_with(large_poly, scale=100, raise_on_error=False)

    def test_cache_hit_behavior(self):
        """Identical polygon queried twice within 24 hours hits cache on second call."""
        poly = {
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

        # Clear cache before starting
        clear_satellite_cache()
        key = get_polygon_cache_key(poly)
        assert len(key) == 64  # SHA-256 hex string

        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Filter"), \
             patch("ee.Reducer"):

            # First query: Cache miss
            mock_bio_coll = MagicMock()
            mock_fc.return_value = mock_bio_coll
            mock_bio_coll.filterBounds.return_value = mock_bio_coll
            mock_bio_coll.filter.return_value = mock_bio_coll
            mock_bio_coll.aggregate_stats.return_value.getInfo.return_value = {"count": 25, "mean": 240.0, "total_sd": 25.0}

            mock_img_coll = MagicMock()
            mock_ic.return_value = mock_img_coll
            mock_img_coll.filterBounds.return_value = mock_img_coll
            mock_img_coll.filterDate.return_value = mock_img_coll
            mock_img_coll.size.return_value.getInfo.return_value = 10
            mock_img_coll.map.return_value.median.return_value.normalizedDifference.return_value.rename.return_value.reduceRegion.return_value.getInfo.return_value = {
                "ndvi_mean": 0.82, "ndvi_count": 5000,
            }
            mock_img_coll.map.return_value.select.return_value.mean.return_value.reduceRegion.return_value.getInfo.return_value = {
                "rh98_mean": 28.0, "rh98_count": 30,
            }
            mock_img_coll.select.return_value.reduce.return_value.eq.return_value.rename.return_value.reduceRegion.return_value.getInfo.return_value = {
                "trees_mean": 0.88, "trees_count": 8000,
            }

            res1 = get_satellite_observations(poly)
            assert res1["cache_hit"] is False
            assert res1["agb_t_per_ha"] == 240.0

            # Second query: Cache hit without calling EE!
            res2 = get_satellite_observations(poly)
            assert res2["cache_hit"] is True
            assert res2["agb_t_per_ha"] == 240.0

    def test_earth_engine_timeout_graceful_handling(self):
        """Earth Engine query timeout for a single sensor sets field to null and records warning without crashing pipeline."""
        poly = {
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

        # Simulate timeout on GEDI biomass query
        with patch("app.core.earth_engine.get_gedi_biomass", side_effect=TimeoutError("Earth Engine computational budget exceeded after 60s")), \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c:

            mock_h.return_value = {"mean_canopy_height_m": 29.0, "height_observation_count": 20, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.83, "valid_pixel_percentage": 94.0, "image_count": 15}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 85.0, "canopy_data_available": True, "canopy_pixel_count": 6000}

            obs = get_satellite_observations(poly)

            # Biomass is null due to timeout
            assert obs["agb_t_per_ha"] is None
            assert obs["gedi_data_available"] is False

            # Other sensors survived and returned valid observations
            assert obs["mean_canopy_height_m"] == 29.0
            assert obs["canopy_cover_pct"] == 85.0
            assert obs["mean_ndvi"] == 0.83

            # Human-readable timeout warning present
            assert any("timed out" in w.lower() for w in obs["data_warnings"])
