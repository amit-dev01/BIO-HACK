"""Unit tests for the biomass calculation module (app/core/biomass.py)."""

from typing import Any, cast

import pytest

from app.core.biomass import (
    DEFAULT_ROOT_TO_SHOOT_RATIOS,
    calculate_below_ground_biomass,
    calculate_total_biomass,
    get_root_to_shoot_ratio,
)


class TestRootToShootRatios:
    """Tests for root-to-shoot ratio lookup and configuration."""

    def test_default_ratios_presence(self):
        assert DEFAULT_ROOT_TO_SHOOT_RATIOS["Tropical Moist Broadleaf"] == 0.21
        assert DEFAULT_ROOT_TO_SHOOT_RATIOS["Temperate Broadleaf"] == 0.26
        assert DEFAULT_ROOT_TO_SHOOT_RATIOS["Boreal Coniferous"] == 0.24
        assert DEFAULT_ROOT_TO_SHOOT_RATIOS["Other"] == 0.23

    @pytest.mark.parametrize(
        "forest_type,expected_ratio",
        [
            ("Tropical Moist Broadleaf", 0.21),
            ("tropical moist broadleaf", 0.21),
            ("TROPICAL_MOIST_BROADLEAF", 0.21),
            ("Temperate Broadleaf", 0.26),
            ("temperate broadleaf", 0.26),
            ("Boreal Coniferous", 0.24),
            ("boreal coniferous", 0.24),
            ("Other", 0.23),
            ("unknown_biome_xyz", 0.23),  # fallback to Other
        ],
    )
    def test_get_ratio_case_insensitivity_and_fallbacks(self, forest_type, expected_ratio):
        assert get_root_to_shoot_ratio(forest_type) == expected_ratio

    def test_custom_ratios_override(self):
        custom = {"Tropical Moist Broadleaf": 0.28, "Custom Mangrove": 0.49, "other": 0.25}
        assert get_root_to_shoot_ratio("Tropical Moist Broadleaf", custom_ratios=custom) == 0.28
        assert get_root_to_shoot_ratio("Custom Mangrove", custom_ratios=custom) == 0.49
        assert get_root_to_shoot_ratio("Unknown Nonexistent", custom_ratios=custom) == 0.25

        # Custom mapping without 'other' falls back to default constant (0.23)
        custom_no_other = {"Pine": 0.3}
        assert get_root_to_shoot_ratio("Unknown Nonexistent", custom_ratios=custom_no_other) == 0.23

    def test_custom_ratio_negative_error(self):
        custom = {"Tropical Moist Broadleaf": -0.1}
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_below_ground_biomass(100.0, "Tropical Moist Broadleaf", custom_ratios=custom)

    def test_non_string_forest_type_raises_type_error(self):
        with pytest.raises(TypeError):
            get_root_to_shoot_ratio(cast(Any, 123))


class TestBelowGroundBiomass:
    """Tests for calculate_below_ground_biomass."""

    def test_tropical_forest_bgb(self):
        # AGB = 200.0 t/ha, Tropical Moist Broadleaf ratio = 0.21 -> BGB = 42.0 t/ha
        agb = 200.0
        bgb = calculate_below_ground_biomass(agb, "Tropical Moist Broadleaf")
        assert pytest.approx(bgb, rel=1e-5) == 42.0

    def test_temperate_forest_bgb(self):
        # AGB = 150.0 t/ha, Temperate Broadleaf ratio = 0.26 -> BGB = 39.0 t/ha
        agb = 150.0
        bgb = calculate_below_ground_biomass(agb, "Temperate Broadleaf")
        assert pytest.approx(bgb, rel=1e-5) == 39.0

    def test_boreal_forest_bgb(self):
        # AGB = 100.0 t/ha, Boreal Coniferous ratio = 0.24 -> BGB = 24.0 t/ha
        agb = 100.0
        bgb = calculate_below_ground_biomass(agb, "Boreal Coniferous")
        assert pytest.approx(bgb, rel=1e-5) == 24.0

    def test_other_forest_bgb(self):
        # AGB = 100.0 t/ha, Other ratio = 0.23 -> BGB = 23.0 t/ha
        agb = 100.0
        bgb = calculate_below_ground_biomass(agb, "Other")
        assert pytest.approx(bgb, rel=1e-5) == 23.0

    def test_zero_biomass(self):
        """Zero above-ground biomass must yield exactly zero below-ground biomass."""
        bgb = calculate_below_ground_biomass(0.0, "Tropical Moist Broadleaf")
        assert bgb == 0.0
        assert isinstance(bgb, float)

    def test_negative_biomass_rejection(self):
        """Negative above-ground biomass must be rejected with ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_below_ground_biomass(-10.0, "Tropical Moist Broadleaf")

    def test_missing_and_invalid_data(self):
        """Missing data (None, NaN, Inf) must raise appropriate errors."""
        with pytest.raises(TypeError):
            calculate_below_ground_biomass(cast(Any, None), "Tropical Moist Broadleaf")

        with pytest.raises(ValueError, match="cannot be NaN"):
            calculate_below_ground_biomass(float("nan"), "Tropical Moist Broadleaf")

        with pytest.raises(ValueError, match="cannot be infinite"):
            calculate_below_ground_biomass(float("inf"), "Tropical Moist Broadleaf")

        with pytest.raises(TypeError):
            calculate_below_ground_biomass(100.0, cast(Any, None))


class TestTotalBiomass:
    """Tests for calculate_total_biomass."""

    def test_total_biomass_calculation(self):
        agb = 150.0
        bgb = 39.0
        total = calculate_total_biomass(agb, bgb)
        assert pytest.approx(total, rel=1e-5) == 189.0
        assert isinstance(total, float)

    def test_zero_biomass_sum(self):
        assert calculate_total_biomass(0.0, 0.0) == 0.0

    def test_negative_biomass_rejection(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_total_biomass(-5.0, 20.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_total_biomass(20.0, -5.0)

    def test_missing_data_rejection(self):
        with pytest.raises(TypeError):
            calculate_total_biomass(cast(Any, None), 20.0)

        with pytest.raises(TypeError):
            calculate_total_biomass(20.0, cast(Any, None))

        with pytest.raises(TypeError):
            calculate_total_biomass(cast(Any, "invalid"), 20.0)

        with pytest.raises(ValueError):
            calculate_total_biomass(float("nan"), 20.0)

        with pytest.raises(ValueError):
            calculate_total_biomass(20.0, float("inf"))
