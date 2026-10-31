"""Unit tests for the confidence assessment module (app/core/confidence.py)."""

from typing import Any, cast

import pytest

from app.core.confidence import (
    assess_confidence,
    calculate_confidence,
)


class TestConfidenceModule:
    """Tests for calculate_confidence and assess_confidence."""

    def test_high_confidence_scenario(self):
        """Dense GEDI shots, low biomass uncertainty, minimal clouds, high classification quality, 0% missing."""
        result = calculate_confidence(
            gedi_shot_count=50,
            biomass_uncertainty_se=8.0,
            agb_t_per_ha=160.0,  # RSE = 5%
            cloud_cover_pct=2.0,
            classification_probability=0.95,
            missing_data_pct=0.0,
        )

        assert 75 <= result["confidence_score"] <= 100
        assert result["confidence_label"] == "High"
        assert result["confidence_interval_pct"] is not None
        assert pytest.approx(result["confidence_interval_pct"], abs=0.01) == 5.0

    def test_medium_confidence_scenario(self):
        """Moderate GEDI shots, moderate cloud cover, acceptable uncertainty."""
        result = calculate_confidence(
            gedi_shot_count=15,
            biomass_uncertainty_se=30.0,
            agb_t_per_ha=100.0,  # RSE = 30%
            cloud_cover_pct=25.0,
            classification_probability=0.70,
            missing_data_pct=5.0,
        )

        assert 50 <= result["confidence_score"] < 75
        assert result["confidence_label"] == "Medium"
        assert result["confidence_interval_pct"] == 30.0

    def test_low_confidence_scenario(self):
        """Very few GEDI shots, high cloud cover, severe missing data."""
        result = calculate_confidence(
            gedi_shot_count=2,
            biomass_uncertainty_se=70.0,
            agb_t_per_ha=80.0,  # RSE = 87.5%
            cloud_cover_pct=80.0,
            classification_probability=0.30,
            missing_data_pct=40.0,
        )

        assert result["confidence_score"] < 50
        assert result["confidence_label"] == "Low"

    def test_missing_uncertainty_returns_none_interval(self):
        """When biomass uncertainty info is unavailable, confidence_interval_pct MUST be None.

        Guardrail: Do not invent uncertainty percentages.
        """
        result = calculate_confidence(
            gedi_shot_count=40,
            biomass_uncertainty_se=None,  # missing SE
            agb_t_per_ha=150.0,
            cloud_cover_pct=5.0,
            classification_probability=0.90,
            missing_data_pct=0.0,
        )

        assert result["confidence_interval_pct"] is None
        assert 0 <= result["confidence_score"] <= 100

    def test_missing_agb_returns_none_interval(self):
        """If AGB is missing or zero with non-zero SE, interval must be None."""
        result = calculate_confidence(
            gedi_shot_count=20,
            biomass_uncertainty_se=15.0,
            agb_t_per_ha=None,  # missing AGB
        )
        assert result["confidence_interval_pct"] is None

    def test_completely_missing_data(self):
        """When all input parameters are None, return score 0 and Low label."""
        result = calculate_confidence()
        assert result["confidence_score"] == 0
        assert result["confidence_label"] == "Low"
        assert result["confidence_interval_pct"] is None

    def test_convenience_wrapper_assess_confidence(self):
        """assess_confidence accepts dictionary and keyword arguments."""
        data = {
            "gedi_shot_count": 35,
            "biomass_uncertainty_se": 10.0,
            "agb_t_per_ha": 100.0,
            "cloud_cover_pct": 10.0,
            "classification_probability": 0.85,
        }
        res_dict = assess_confidence(data)
        res_kwargs = assess_confidence(**data)

        assert res_dict["confidence_score"] == res_kwargs["confidence_score"]
        assert res_dict["confidence_label"] == res_kwargs["confidence_label"]
        assert res_dict["confidence_interval_pct"] == 10.0

    def test_gedi_coverage_pct_direct(self):
        """Test providing gedi_coverage_pct directly."""
        result = calculate_confidence(
            gedi_coverage_pct=80.0,
            biomass_uncertainty_se=10.0,
            agb_t_per_ha=100.0,
        )
        assert result["confidence_score"] > 0
        assert result["confidence_interval_pct"] == 10.0

    def test_zero_biomass_with_zero_se(self):
        """Zero biomass with zero standard error."""
        result = calculate_confidence(
            gedi_shot_count=20,
            biomass_uncertainty_se=0.0,
            agb_t_per_ha=0.0,
        )
        assert result["confidence_interval_pct"] == 0.0

    def test_zero_biomass_with_positive_se(self):
        """Zero biomass with non-zero standard error."""
        result = calculate_confidence(
            gedi_shot_count=20,
            biomass_uncertainty_se=5.0,
            agb_t_per_ha=0.0,
        )
        assert result["confidence_interval_pct"] is None

    def test_rse_between_50_and_100_percent(self):
        result = calculate_confidence(
            gedi_shot_count=30,
            biomass_uncertainty_se=75.0,
            agb_t_per_ha=100.0,  # 75% RSE
            cloud_cover_pct=10.0,
        )
        assert result["confidence_interval_pct"] == 75.0

    def test_rse_greater_than_100_percent(self):
        result = calculate_confidence(
            gedi_shot_count=30,
            biomass_uncertainty_se=150.0,
            agb_t_per_ha=100.0,  # 150% RSE
        )
        assert result["confidence_interval_pct"] == 150.0

    def test_classification_percentage_format_and_errors(self):
        """Classification can be 0.0-1.0 or 0.0-100.0."""
        res_pct = calculate_confidence(classification_probability=85.0)
        res_prob = calculate_confidence(classification_probability=0.85)
        assert res_pct["confidence_score"] == res_prob["confidence_score"]

        with pytest.raises(ValueError, match="must be <= 1.0"):
            calculate_confidence(classification_probability=105.0)

        with pytest.raises(ValueError):
            calculate_confidence(classification_probability=-0.1)

    def test_severe_missing_data_penalty(self):
        """More than 50% missing data applies a heavy penalty factor."""
        result_normal = calculate_confidence(
            gedi_shot_count=30,
            biomass_uncertainty_se=10.0,
            agb_t_per_ha=100.0,
            missing_data_pct=10.0,
        )
        result_severe = calculate_confidence(
            gedi_shot_count=30,
            biomass_uncertainty_se=10.0,
            agb_t_per_ha=100.0,
            missing_data_pct=80.0,
        )
        assert result_severe["confidence_score"] < result_normal["confidence_score"]

    def test_nan_and_inf_inputs_rejected(self):
        with pytest.raises(ValueError):
            calculate_confidence(biomass_uncertainty_se=float("nan"))
        with pytest.raises(ValueError):
            calculate_confidence(biomass_uncertainty_se=float("inf"))
        with pytest.raises(ValueError):
            calculate_confidence(agb_t_per_ha=float("nan"))
        with pytest.raises(ValueError):
            calculate_confidence(agb_t_per_ha=float("inf"))
        with pytest.raises(ValueError):
            calculate_confidence(classification_probability=float("nan"))
        with pytest.raises(ValueError):
            calculate_confidence(classification_probability=float("inf"))
        with pytest.raises(ValueError):
            calculate_confidence(cloud_cover_pct=float("nan"))
        with pytest.raises(ValueError):
            calculate_confidence(cloud_cover_pct=float("inf"))

    def test_invalid_negative_and_out_of_bounds_inputs(self):
        """Invalid negative values or percentages outside [0, 100] raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_confidence(gedi_shot_count=-5)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_confidence(biomass_uncertainty_se=-2.0)

        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_confidence(agb_t_per_ha=-10.0)

        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            calculate_confidence(cloud_cover_pct=-1.0)

        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            calculate_confidence(cloud_cover_pct=105.0)

        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            calculate_confidence(missing_data_pct=-10.0)

        with pytest.raises(ValueError, match="between 0.0 and 100.0"):
            calculate_confidence(missing_data_pct=101.0)

    def test_invalid_types_raise_type_error(self):
        with pytest.raises(TypeError):
            calculate_confidence(gedi_shot_count=cast(Any, "twenty"))

        with pytest.raises(TypeError):
            calculate_confidence(cloud_cover_pct=cast(Any, "low"))

        with pytest.raises(TypeError):
            calculate_confidence(biomass_uncertainty_se=cast(Any, "invalid"))

        with pytest.raises(TypeError):
            calculate_confidence(agb_t_per_ha=cast(Any, "invalid"))

        with pytest.raises(TypeError):
            calculate_confidence(classification_probability=cast(Any, "invalid"))
