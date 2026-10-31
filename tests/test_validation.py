"""Unit tests for satellite data validation and cross-validation layer (Phase 4).

Covers:
1. Negative biomass rejection (agbd < 0)
2. Impossibly high biomass rejection (agbd > 1000 Mg/ha)
3. Quality flag rejection (l4_quality_flag != 1, degrade_flag != 0)
4. Negative height rejection (height < 0 m)
5. Impossibly tall height rejection (height > 120 m)
6. Invalid NDVI range rejection (< -0.2 and > 1.0)
7. Cross-validation consistency detection:
   - Biomass vs Canopy Cover (> 400 t/ha with < 30% canopy)
   - Biomass vs Height (> 300 t/ha with < 10 m height)
   - NDVI vs Canopy Cover (> 0.8 NDVI with < 20% canopy)
   - Forest Type vs Biomass (Boreal Coniferous with > 500 t/ha)
8. Uncertainty quantification and confidence interval calculation (95% CI)
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.earth_engine import (
    cross_validate_satellite_observations,
    get_gedi_biomass,
    get_gedi_canopy_height,
    get_satellite_observations,
    validate_canopy_cover,
    validate_gedi_biomass_dataset,
    validate_gedi_biomass_observation,
    validate_gedi_height_dataset,
    validate_gedi_height_observation,
    validate_ndvi_value,
)


@pytest.fixture
def amazon_polygon():
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.0, -3.0],
                [-60.0, -2.9],
                [-59.9, -2.9],
                [-59.9, -3.0],
                [-60.0, -3.0],
            ]
        ],
    }


class TestBiomassValidation:
    """Tests checking physical bounds and quality criteria for GEDI biomass observations."""

    def test_negative_biomass_observation_rejected(self):
        """Negative biomass is physically impossible and must be rejected."""
        ok, reason = validate_gedi_biomass_observation(agbd=-15.4)
        assert not ok
        assert reason is not None
        assert "cannot be negative" in reason

    def test_impossibly_high_biomass_rejected(self):
        """Biomass > 1000 Mg/ha exceeds biological limits on Earth and must be rejected."""
        ok, reason = validate_gedi_biomass_observation(agbd=1250.0)
        assert not ok
        assert reason is not None
        assert "1000 Mg/ha" in reason

    def test_low_quality_flag_rejected(self):
        """Observations with l4_quality_flag != 1 or degrade_flag != 0 are rejected."""
        ok_qual, reason_qual = validate_gedi_biomass_observation(agbd=150.0, l4_quality_flag=0)
        assert not ok_qual
        assert reason_qual is not None
        assert "l4_quality_flag" in reason_qual

        ok_deg, reason_deg = validate_gedi_biomass_observation(agbd=150.0, degrade_flag=1)
        assert not ok_deg
        assert reason_deg is not None
        assert "degrade_flag" in reason_deg

    def test_valid_biomass_observation_accepted(self):
        """Realistic biomass observation with valid quality flags passes."""
        ok, reason = validate_gedi_biomass_observation(agbd=240.0, l4_quality_flag=1, degrade_flag=0)
        assert ok
        assert reason is None

    def test_dataset_validation_separates_counts(self):
        """Dataset validator counts valid and rejected footprints separately."""
        raw_obs = [
            {"agbd": 200.0, "l4_quality_flag": 1, "degrade_flag": 0},
            {"agbd": -50.0, "l4_quality_flag": 1, "degrade_flag": 0},  # rejected: negative
            {"agbd": 1200.0, "l4_quality_flag": 1, "degrade_flag": 0},  # rejected: > 1000
            {"agbd": 300.0, "l4_quality_flag": 0, "degrade_flag": 0},  # rejected: quality
            {"agbd": 250.0, "l4_quality_flag": 1, "degrade_flag": 0},  # valid
        ]
        res = validate_gedi_biomass_dataset(raw_obs)
        assert res["valid_observation_count"] == 2
        assert res["rejected_observation_count"] == 3
        assert len(res["rejection_reasons"]) >= 3
        assert res["gedi_data_available"] is True
        assert res["mean_agbd"] == 225.0

    def test_all_rejected_observations_returns_null_biomass(self, amazon_polygon):
        """When all observations fail validation, returns null without default fallback."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter"):

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            # Mock return indicating mean is out of physical bounds (> 1000)
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {
                "count": 5,
                "mean": 1500.0,
                "total_sd": 20.0,
            }

            res = get_gedi_biomass(amazon_polygon)
            assert res["agb_t_per_ha"] is None
            assert res["gedi_data_available"] is False
            assert res["valid_observation_count"] == 0
            assert res["rejected_observation_count"] >= 5


class TestCanopyHeightValidation:
    """Tests checking physical bounds and quality criteria for GEDI canopy height observations."""

    def test_negative_height_rejected(self):
        """Negative canopy height is physically impossible and must be rejected."""
        ok, reason = validate_gedi_height_observation(height_m=-5.0)
        assert not ok
        assert reason is not None
        assert "cannot be negative" in reason

    def test_impossibly_tall_height_rejected(self):
        """Heights > 120m exceed the tallest known living tree (~116m) and must be rejected."""
        ok, reason = validate_gedi_height_observation(height_m=135.0)
        assert not ok
        assert reason is not None
        assert "120 m" in reason

    def test_height_quality_flags_enforced(self):
        """Observations with degraded instrument flags are rejected."""
        ok_q, reason_q = validate_gedi_height_observation(height_m=35.0, quality_flag=0)
        assert not ok_q
        assert reason_q is not None
        assert "quality_flag" in reason_q

        ok_d, reason_d = validate_gedi_height_observation(height_m=35.0, degrade_flag=1)
        assert not ok_d
        assert reason_d is not None
        assert "degrade_flag" in reason_d

    def test_height_dataset_validation(self):
        """Height dataset validator tallies valid and rejected counts correctly."""
        obs = [25.0, 32.0, -4.0, 140.0, 41.0]
        res = validate_gedi_height_dataset(obs)
        assert res["valid_height_count"] == 3
        assert res["rejected_height_count"] == 2
        assert res["height_data_available"] is True
        assert pytest.approx(res["mean_canopy_height_m"], 0.1) == 32.7

    def test_all_rejected_heights_returns_null(self, amazon_polygon):
        """When all heights are rejected, returns null mean_canopy_height_m."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 10
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_mean_img = MagicMock()
            mock_masked.select.return_value.mean.return_value = mock_mean_img
            # Impossibly tall height reported in stats
            mock_mean_img.reduceRegion.return_value.getInfo.return_value = {
                "rh98_mean": 145.0,
                "rh98_count": 12,
            }

            res = get_gedi_canopy_height(amazon_polygon)
            assert res["mean_canopy_height_m"] is None
            assert res["height_data_available"] is False
            assert res["valid_height_count"] == 0
            assert res["rejected_height_count"] >= 12


class TestNdviAndCanopyValidation:
    """Tests checking bounds and validity for Sentinel-2 NDVI and Dynamic World canopy cover."""

    def test_ndvi_out_of_range_rejected(self):
        """NDVI values outside [-0.2, 1.0] are rejected."""
        ok_low, val_low, w_low = validate_ndvi_value(-0.5)
        assert not ok_low
        assert val_low is None
        assert any("rejected" in w for w in w_low)

        ok_high, val_high, w_high = validate_ndvi_value(1.2)
        assert not ok_high
        assert val_high is None
        assert any("rejected" in w for w in w_high)

    def test_ndvi_sparse_vegetation_flagged(self):
        """NDVI < 0.2 is valid but flagged as sparse vegetation."""
        ok, val, warns = validate_ndvi_value(0.12, is_water_or_urban=False)
        assert ok
        assert val == 0.12
        assert any("sparse vegetation" in w.lower() for w in warns)

    def test_canopy_cover_bounds(self):
        """Canopy cover must be between 0 and 100%."""
        ok_neg, _, w_neg = validate_canopy_cover(-5.0)
        assert not ok_neg
        assert any("outside bounds" in w for w in w_neg)

        ok_high, _, w_high = validate_canopy_cover(105.0)
        assert not ok_high
        assert any("outside bounds" in w for w in w_high)

    def test_canopy_cover_near_100_low_ndvi_warning(self):
        """Canopy cover > 99% with NDVI < 0.5 triggers discrepancy warning."""
        ok, val, warns = validate_canopy_cover(99.5, mean_ndvi=0.35)
        assert ok
        assert val == 99.5
        assert any("discrepancy" in w for w in warns)

    def test_canopy_cover_under_5_pct_flagged_likely_non_forest(self):
        """Canopy cover < 5% is flagged as likely non-forest."""
        ok, val, warns = validate_canopy_cover(3.2, mean_ndvi=0.25)
        assert ok
        assert val == 3.2
        assert any("likely non-forest" in w for w in warns)


class TestCrossValidationInconsistencies:
    """Tests multi-sensor cross-validation inconsistency checks."""

    def test_check1_biomass_vs_canopy_cover(self):
        """Biomass > 400 t/ha with canopy < 30% flags inconsistency."""
        warns = cross_validate_satellite_observations(
            agb_t_per_ha=450.0,
            canopy_cover_pct=22.0,
            mean_canopy_height_m=32.0,
            mean_ndvi=0.82,
            forest_type="Tropical Moist Broadleaf",
        )
        assert any("High biomass (> 400 t/ha)" in w for w in warns)

    def test_check2_biomass_vs_height(self):
        """Biomass > 300 t/ha with height < 10m flags inconsistency."""
        warns = cross_validate_satellite_observations(
            agb_t_per_ha=320.0,
            canopy_cover_pct=85.0,
            mean_canopy_height_m=7.5,
            mean_ndvi=0.82,
            forest_type="Tropical Moist Broadleaf",
        )
        assert any("High biomass (> 300 t/ha)" in w for w in warns)

    def test_check3_ndvi_vs_canopy_cover(self):
        """NDVI > 0.8 with canopy < 20% flags grassland/cropland inconsistency."""
        warns = cross_validate_satellite_observations(
            agb_t_per_ha=50.0,
            canopy_cover_pct=15.0,
            mean_canopy_height_m=12.0,
            mean_ndvi=0.85,
            forest_type="Temperate Broadleaf",
        )
        assert any("High greenness (NDVI > 0.8)" in w for w in warns)

    def test_check4_forest_type_vs_biomass(self):
        """Boreal forest with biomass > 500 t/ha flags unusual data."""
        warns = cross_validate_satellite_observations(
            agb_t_per_ha=550.0,
            canopy_cover_pct=75.0,
            mean_canopy_height_m=28.0,
            mean_ndvi=0.65,
            forest_type="Boreal Coniferous",
        )
        assert any("Boreal Coniferous" in w and "unusually high" in w for w in warns)

    def test_consistent_observations_produce_no_cross_validation_warnings(self):
        """Typical healthy tropical forest produces empty warning list."""
        warns = cross_validate_satellite_observations(
            agb_t_per_ha=280.0,
            canopy_cover_pct=88.0,
            mean_canopy_height_m=32.0,
            mean_ndvi=0.84,
            forest_type="Tropical Moist Broadleaf",
        )
        assert len(warns) == 0


class TestUncertaintyQuantification:
    """Tests 95% confidence interval and sampling adequacy quantification."""

    def test_confidence_interval_sufficient_observations(self, amazon_polygon):
        """When n >= 5, calculates 95% CI as percentage of mean."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_b, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.forest_classifier.classify_forest_type") as mock_cl:

            # n = 25, mean = 200, stddev = 40
            # CI = 1.96 * (40 / sqrt(25)) = 1.96 * 8 = 15.68 t/ha
            # CI_pct = (15.68 / 200) * 100 = 7.84% -> rounded to nearest integer = 8%
            mock_b.return_value = {
                "agb_t_per_ha": 200.0,
                "agb_stddev": 40.0,
                "gedi_observation_count": 25,
                "valid_observation_count": 25,
                "rejected_observation_count": 0,
                "gedi_data_available": True,
            }
            mock_h.return_value = {"mean_canopy_height_m": 30.0, "height_observation_count": 30, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.85, "valid_pixel_percentage": 95.0, "image_count": 12}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 90.0, "canopy_data_available": True, "canopy_pixel_count": 1000}
            mock_cl.return_value = {
                "forest_type": "Tropical Moist Broadleaf", "ecoregion": "Tropical/Subtropical",
                "dominant_land_cover": "Tree cover", "classification_method": "satellite+latitude",
                "classification_confidence": "high", "recommended_standard": "Verra VM0047",
            }

            res = get_satellite_observations(amazon_polygon)
            unc = res["uncertainty"]
            assert unc["confidence_interval_pct"] == 8
            assert unc["confidence_interval_method"] == "z-score (95% CI)"
            assert unc["sampling_adequacy"] == "sufficient"

    def test_insufficient_gedi_observations_yields_null_ci(self, amazon_polygon):
        """When n < 5, sets confidence_interval_pct to None and marks sampling limited."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_b, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_h, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_t, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_c, \
             patch("app.core.forest_classifier.classify_forest_type") as mock_cl:

            mock_b.return_value = {
                "agb_t_per_ha": 150.0,
                "agb_stddev": 35.0,
                "gedi_observation_count": 3,
                "valid_observation_count": 3,
                "rejected_observation_count": 0,
                "gedi_data_available": True,
            }
            mock_h.return_value = {"mean_canopy_height_m": 25.0, "height_observation_count": 4, "height_data_available": True}
            mock_s.return_value = {"mean_ndvi": 0.78, "valid_pixel_percentage": 88.0, "image_count": 8}
            mock_t.return_value = []
            mock_c.return_value = {"canopy_cover_pct": 75.0, "canopy_data_available": True, "canopy_pixel_count": 500}
            mock_cl.return_value = {
                "forest_type": "Tropical Moist Broadleaf", "ecoregion": "Tropical/Subtropical",
                "dominant_land_cover": "Tree cover", "classification_method": "satellite+latitude",
                "classification_confidence": "medium", "recommended_standard": "Verra VM0047",
            }

            res = get_satellite_observations(amazon_polygon)
            unc = res["uncertainty"]
            assert unc["confidence_interval_pct"] is None
            assert unc["confidence_interval_method"] is None
            assert unc["sampling_adequacy"] == "limited"
