"""Confidence assessment module for CanopyAI.

Evaluates data quality and scientific confidence for forest carbon estimates
combining NASA GEDI, ESA Sentinel-2, and Google Dynamic World data.

Scientific Guardrails:
- A heuristic confidence score is NOT a statistically validated confidence interval.
- Uncertainty percentages are strictly derived from empirical data (e.g., GEDI L4A standard errors).
- Never invent uncertainty percentages: if uncertainty parameters are unavailable,
  confidence_interval_pct returns None (null).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any, TypedDict


class ConfidenceResult(TypedDict):
    confidence_score: int
    confidence_label: str
    confidence_interval_pct: float | None


# Weight distribution for heuristic data quality assessment (sum = 1.0)
WEIGHT_GEDI_AVAILABILITY = 0.30
WEIGHT_BIOMASS_UNCERTAINTY = 0.25
WEIGHT_CLOUD_COVER = 0.20
WEIGHT_CLASSIFICATION_QUALITY = 0.15
WEIGHT_COMPLETENESS = 0.10

# Shot density threshold for full GEDI score in screening area
_GEDI_FULL_SCORE_SHOTS = 30


def _validate_bounded_pct(value: float | None, name: str) -> float | None:
    """Validate that a percentage value is between 0.0 and 100.0 if not None."""
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric, got {type(value).__name__}.")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} cannot be NaN or infinite.")
    if value < 0.0 or value > 100.0:
        raise ValueError(f"{name} must be between 0.0 and 100.0 (got {value}).")
    return float(value)


def calculate_confidence(
    gedi_shot_count: int | None = None,
    gedi_coverage_pct: float | None = None,
    biomass_uncertainty_se: float | None = None,
    agb_t_per_ha: float | None = None,
    cloud_cover_pct: float | None = None,
    classification_probability: float | None = None,
    missing_data_pct: float | None = None,
) -> ConfidenceResult:
    """Assess data quality and determine confidence score, label, and empirical confidence interval.

    Args:
        gedi_shot_count: Number of valid NASA GEDI laser shots within the polygon.
        gedi_coverage_pct: Percentage of polygon covered by GEDI observations (0 to 100).
        biomass_uncertainty_se: Standard error of biomass density in t/ha (from GEDI L4A agbd_se).
        agb_t_per_ha: Mean above-ground biomass density in t/ha. Required to compute relative CI.
        cloud_cover_pct: Percentage of cloud cover in Sentinel-2 imagery (0 to 100).
        classification_probability: Dynamic World / LULC classification confidence (0 to 1 or 0 to 100).
        missing_data_pct: Percentage of the area with no valid satellite data (0 to 100).

    Returns:
        ConfidenceResult containing:
            - confidence_score: integer between 0 and 100
            - confidence_label: "High", "Medium", or "Low"
            - confidence_interval_pct: optional float representing empirical relative uncertainty (%) or None

    Raises:
        ValueError: If input values are out of valid bounds (e.g., negative shots or percentages outside [0, 100]).
        TypeError: If invalid types are provided.
    """
    # 1. Validate inputs
    if gedi_shot_count is not None:
        if not isinstance(gedi_shot_count, int):
            raise TypeError(f"gedi_shot_count must be an integer, got {type(gedi_shot_count).__name__}.")
        if gedi_shot_count < 0:
            raise ValueError(f"gedi_shot_count cannot be negative (got {gedi_shot_count}).")

    validated_gedi_cov = _validate_bounded_pct(gedi_coverage_pct, "gedi_coverage_pct")
    validated_cloud_cov = _validate_bounded_pct(cloud_cover_pct, "cloud_cover_pct")
    validated_missing_pct = _validate_bounded_pct(missing_data_pct, "missing_data_pct")

    if biomass_uncertainty_se is not None:
        if not isinstance(biomass_uncertainty_se, (int, float)):
            raise TypeError("biomass_uncertainty_se must be numeric.")
        if math.isnan(biomass_uncertainty_se) or math.isinf(biomass_uncertainty_se):
            raise ValueError("biomass_uncertainty_se cannot be NaN or infinite.")
        if biomass_uncertainty_se < 0.0:
            raise ValueError(f"biomass_uncertainty_se cannot be negative (got {biomass_uncertainty_se}).")

    if agb_t_per_ha is not None:
        if not isinstance(agb_t_per_ha, (int, float)):
            raise TypeError("agb_t_per_ha must be numeric.")
        if math.isnan(agb_t_per_ha) or math.isinf(agb_t_per_ha):
            raise ValueError("agb_t_per_ha cannot be NaN or infinite.")
        if agb_t_per_ha < 0.0:
            raise ValueError(f"agb_t_per_ha cannot be negative (got {agb_t_per_ha}).")

    validated_class_prob: float | None = None
    if classification_probability is not None:
        if not isinstance(classification_probability, (int, float)):
            raise TypeError("classification_probability must be numeric.")
        if math.isnan(classification_probability) or math.isinf(classification_probability):
            raise ValueError("classification_probability cannot be NaN or infinite.")
        if classification_probability < 0.0:
            raise ValueError("classification_probability cannot be negative.")
        # Normalize to 0-100 range
        if classification_probability <= 1.0:
            validated_class_prob = classification_probability * 100.0
        elif classification_probability <= 100.0:
            validated_class_prob = float(classification_probability)
        else:
            raise ValueError(f"classification_probability must be <= 1.0 (or <= 100%), got {classification_probability}")

    # Check if all inputs are None (completely missing data)
    all_none = (
        gedi_shot_count is None
        and validated_gedi_cov is None
        and biomass_uncertainty_se is None
        and agb_t_per_ha is None
        and validated_cloud_cov is None
        and validated_class_prob is None
        and validated_missing_pct is None
    )
    if all_none:
        return {
            "confidence_score": 0,
            "confidence_label": "Low",
            "confidence_interval_pct": None,
        }

    # 2. Evaluate GEDI Availability Component (0 to 100)
    gedi_score = 0.0
    if validated_gedi_cov is not None:
        gedi_score = validated_gedi_cov
    elif gedi_shot_count is not None:
        gedi_score = min(100.0, (gedi_shot_count / _GEDI_FULL_SCORE_SHOTS) * 100.0)

    # 3. Evaluate Biomass Uncertainty Component (0 to 100) & Empirical CI
    biomass_score = 0.0
    confidence_interval_pct: float | None = None

    if biomass_uncertainty_se is not None and agb_t_per_ha is not None and agb_t_per_ha > 0.0:
        # Calculate empirical Relative Standard Error (% RSE)
        relative_se_pct = (biomass_uncertainty_se / agb_t_per_ha) * 100.0
        confidence_interval_pct = round(relative_se_pct, 2)

        # Scientific quality curve: RSE <= 10% is top-tier; > 60% is low quality
        if relative_se_pct <= 10.0:
            biomass_score = 100.0
        elif relative_se_pct <= 50.0:
            # Linear interpolation from 100 down to 40
            biomass_score = 100.0 - ((relative_se_pct - 10.0) / 40.0) * 60.0
        elif relative_se_pct <= 100.0:
            # Linear interpolation from 40 down to 0
            biomass_score = max(0.0, 40.0 - ((relative_se_pct - 50.0) / 50.0) * 40.0)
        else:
            biomass_score = 0.0
    elif biomass_uncertainty_se is not None and agb_t_per_ha == 0.0:
        # Zero biomass with zero standard error
        if biomass_uncertainty_se == 0.0:
            biomass_score = 100.0
            confidence_interval_pct = 0.0
        else:
            biomass_score = 20.0
            confidence_interval_pct = None
    else:
        # Insufficient uncertainty information: do NOT invent uncertainty percentages
        confidence_interval_pct = None
        # Default neutral/low score for missing uncertainty metric
        biomass_score = 20.0 if (agb_t_per_ha is not None and agb_t_per_ha > 0) else 0.0

    # 4. Evaluate Cloud Coverage Component (0 to 100)
    cloud_score = 0.0
    if validated_cloud_cov is not None:
        cloud_score = max(0.0, 100.0 - validated_cloud_cov)
    else:
        cloud_score = 50.0  # Moderate default when cloud coverage metadata is not available

    # 5. Evaluate Classification Quality Component (0 to 100)
    class_score = 0.0
    if validated_class_prob is not None:
        class_score = validated_class_prob
    else:
        class_score = 50.0  # Moderate default when probability layer is not provided

    # 6. Evaluate Completeness Component (0 to 100)
    completeness_score = 100.0
    if validated_missing_pct is not None:
        completeness_score = max(0.0, 100.0 - validated_missing_pct)

    # 7. Aggregate weighted score
    raw_score = (
        WEIGHT_GEDI_AVAILABILITY * gedi_score
        + WEIGHT_BIOMASS_UNCERTAINTY * biomass_score
        + WEIGHT_CLOUD_COVER * cloud_score
        + WEIGHT_CLASSIFICATION_QUALITY * class_score
        + WEIGHT_COMPLETENESS * completeness_score
    )

    # Apply heavy penalty if missing data percentage is severe (> 50%)
    if validated_missing_pct is not None and validated_missing_pct > 50.0:
        penalty_factor = (100.0 - validated_missing_pct) / 50.0
        raw_score *= max(0.0, penalty_factor)

    confidence_score = max(0, min(100, round(raw_score)))

    # 8. Map to label
    if confidence_score >= 75:
        confidence_label = "High"
    elif confidence_score >= 50:
        confidence_label = "Medium"
    else:
        confidence_label = "Low"

    return {
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "confidence_interval_pct": confidence_interval_pct,
    }


def assess_confidence(
    data: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> ConfidenceResult:
    """Convenience wrapper for calculate_confidence accepting dict or kwargs.

    Args:
        data: Optional dictionary containing confidence parameters.
        **kwargs: Keyword arguments matching calculate_confidence parameters.

    Returns:
        ConfidenceResult dictionary.
    """
    merged_params: dict[str, Any] = {}
    if data:
        merged_params.update(data)
    merged_params.update(kwargs)

    return calculate_confidence(
        gedi_shot_count=merged_params.get("gedi_shot_count"),
        gedi_coverage_pct=merged_params.get("gedi_coverage_pct"),
        biomass_uncertainty_se=merged_params.get("biomass_uncertainty_se"),
        agb_t_per_ha=merged_params.get("agb_t_per_ha"),
        cloud_cover_pct=merged_params.get("cloud_cover_pct"),
        classification_probability=merged_params.get("classification_probability"),
        missing_data_pct=merged_params.get("missing_data_pct"),
    )


def calculate_confidence_score(
    observations_or_data: Mapping[str, Any] | None = None,
    area_ha: float | None = None,
    **kwargs: Any,
) -> ConfidenceResult:
    """Assess overall data quality and calculate confidence score (0-100) and grade.

    Applies Phase 4 uncertainty rules:
      - Evaluates GEDI footprint sampling density (<5: high penalty, 5-20: moderate penalty)
      - Coefficient of variation (CV = stddev / mean > 0.5) penalizes high heterogenity
      - Cloud cover > 30% reduces confidence
      - Area adjustments: 10-50 ha reduces score by 10; > 50,000 ha reduces score by 5
      - Low classification confidence reduces score by 15
      - Water/ocean or complete data failure produces score 0 ("Low")

    Labelled clearly as a data quality indicator rather than a formal statistical CI.
    """
    merged: dict[str, Any] = {}
    if observations_or_data is not None:
        merged.update(observations_or_data)
    merged.update(kwargs)

    # Detect complete data failure or ocean
    data_warnings = merged.get("data_warnings", [])
    forest_type = merged.get("forest_type")
    is_water = (
        forest_type == "Non-Forest"
        and any("water" in str(w).lower() for w in data_warnings)
    )
    all_nulls = (
        merged.get("agb_t_per_ha") is None
        and merged.get("mean_ndvi") is None
        and merged.get("canopy_cover_pct") is None
        and merged.get("mean_canopy_height_m") is None
    )
    if is_water or (all_nulls and "gedi_shot_count" not in merged):
        return {
            "confidence_score": 0,
            "confidence_label": "Low",
            "confidence_interval_pct": None,
        }

    # Extract parameters for standard calculate_confidence
    gedi_count = (
        merged.get("gedi_observation_count")
        or merged.get("valid_gedi_biomass_count")
        or merged.get("gedi_shot_count")
    )
    agb_mean = merged.get("agb_t_per_ha")
    stddev = (
        merged.get("agb_stddev")
        or merged.get("biomass_uncertainty_se")
    )
    cloud_cov = (
        merged.get("validation_summary", {}).get("cloud_masked_pixel_pct")
        if isinstance(merged.get("validation_summary"), dict)
        else merged.get("cloud_cover_pct")
    )
    if cloud_cov is None and merged.get("valid_pixel_percentage") is not None:
        cloud_cov = max(0.0, 100.0 - float(merged["valid_pixel_percentage"]))

    class_prob = merged.get("classification_probability")
    class_conf = merged.get("classification_confidence")
    if class_prob is None and class_conf:
        class_prob = 0.90 if class_conf == "high" else (0.60 if class_conf == "medium" else 0.30)

    missing_pct = merged.get("missing_data_pct")

    # Baseline score calculation
    base_res = calculate_confidence(
        gedi_shot_count=gedi_count,
        gedi_coverage_pct=merged.get("gedi_coverage_pct"),
        biomass_uncertainty_se=stddev,
        agb_t_per_ha=agb_mean,
        cloud_cover_pct=cloud_cov,
        classification_probability=class_prob,
        missing_data_pct=missing_pct,
    )

    score = base_res["confidence_score"]

    # Phase 4 adjustments:
    # A. GEDI Sampling adequacy penalty
    if gedi_count is not None and gedi_count < 5:
        score -= 15
    elif gedi_count is not None and gedi_count < 20:
        score -= 5

    # B. High variance penalty (CV > 0.5)
    if agb_mean and stddev and agb_mean > 0:
        cv = stddev / agb_mean
        if cv > 0.5:
            score -= 10

    # C. Cloud contamination penalty (> 30% clouds)
    if cloud_cov is not None and cloud_cov > 30.0:
        score -= 10

    # D. Area adjustments
    eval_area = area_ha or merged.get("area_ha")
    if eval_area is not None:
        if 10.0 <= eval_area <= 50.0:
            score -= 10
        elif eval_area > 50_000.0:
            score -= 5

    # E. Classification uncertainty
    if class_conf == "low":
        score -= 15

    final_score = max(0, min(100, score))
    if final_score >= 75:
        final_label = "High"
    elif final_score >= 50:
        final_label = "Medium"
    else:
        final_label = "Low"

    return {
        "confidence_score": final_score,
        "confidence_label": final_label,
        "confidence_interval_pct": base_res["confidence_interval_pct"],
    }
