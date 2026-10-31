"""Unit tests for the carbon calculation module (app/core/carbon.py)."""

from typing import Any, cast

import pytest

from app.core.carbon import (
    CARBON_FRACTION,
    CO2_TO_CARBON_RATIO,
    calculate_carbon_stock,
    calculate_co2_equivalent,
    calculate_total_co2,
)


class TestCarbonCalculations:
    """Tests for carbon stock and CO2 equivalent conversions."""

    def test_constants(self):
        assert CARBON_FRACTION == 0.47
        assert pytest.approx(CO2_TO_CARBON_RATIO, rel=1e-5) == 44.0 / 12.0

    def test_calculate_carbon_stock(self):
        # 100.0 t/ha total biomass * 0.47 = 47.0 t C/ha
        total_biomass = 100.0
        carbon_stock = calculate_carbon_stock(total_biomass)
        assert pytest.approx(carbon_stock, rel=1e-5) == 47.0
        assert isinstance(carbon_stock, float)

    def test_calculate_co2_equivalent(self):
        # 12.0 t C/ha * (44 / 12) = 44.0 t CO2e/ha
        carbon_t_per_ha = 12.0
        co2e = calculate_co2_equivalent(carbon_t_per_ha)
        assert pytest.approx(co2e, rel=1e-5) == 44.0
        assert isinstance(co2e, float)

    def test_calculate_total_co2(self):
        # 50.0 t CO2e/ha across 200.0 hectares = 10,000.0 t CO2e
        co2e_per_ha = 50.0
        area_ha = 200.0
        total_co2 = calculate_total_co2(co2e_per_ha, area_ha)
        assert pytest.approx(total_co2, rel=1e-5) == 10_000.0
        assert isinstance(total_co2, float)

    def test_full_pipeline_consistency(self):
        """Test full biomass -> carbon -> CO2e -> total CO2 chain."""
        total_biomass = 200.0  # t/ha
        area_ha = 100.0        # ha

        c_stock = calculate_carbon_stock(total_biomass)
        assert pytest.approx(c_stock) == 94.0

        co2e_ha = calculate_co2_equivalent(c_stock)
        expected_co2e_ha = 94.0 * (44.0 / 12.0)
        assert pytest.approx(co2e_ha) == expected_co2e_ha

        total_co2 = calculate_total_co2(co2e_ha, area_ha)
        assert pytest.approx(total_co2) == expected_co2e_ha * 100.0


class TestCarbonEdgeCasesAndRejections:
    """Tests for zero biomass, negative values, and missing data."""

    def test_zero_values(self):
        assert calculate_carbon_stock(0.0) == 0.0
        assert calculate_co2_equivalent(0.0) == 0.0
        assert calculate_total_co2(0.0, 100.0) == 0.0
        assert calculate_total_co2(50.0, 0.0) == 0.0
        assert calculate_total_co2(0.0, 0.0) == 0.0

    def test_negative_value_rejections(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_carbon_stock(-1.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_co2_equivalent(-5.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_total_co2(-10.0, 100.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_total_co2(10.0, -100.0)

    def test_missing_data_rejections(self):
        with pytest.raises(TypeError):
            calculate_carbon_stock(cast(Any, None))

        with pytest.raises(TypeError):
            calculate_carbon_stock(cast(Any, "invalid"))

        with pytest.raises(TypeError):
            calculate_co2_equivalent(cast(Any, None))

        with pytest.raises(TypeError):
            calculate_co2_equivalent(cast(Any, "invalid"))

        with pytest.raises(TypeError):
            calculate_total_co2(cast(Any, None), 100.0)

        with pytest.raises(TypeError):
            calculate_total_co2(100.0, cast(Any, None))

        with pytest.raises(TypeError):
            calculate_total_co2(cast(Any, "invalid"), 100.0)

        with pytest.raises(ValueError, match="cannot be NaN"):
            calculate_carbon_stock(float("nan"))

        with pytest.raises(ValueError, match="cannot be infinite"):
            calculate_carbon_stock(float("inf"))

        with pytest.raises(ValueError, match="cannot be infinite"):
            calculate_co2_equivalent(float("inf"))

        with pytest.raises(ValueError, match="cannot be infinite"):
            calculate_total_co2(100.0, float("inf"))
