"""Biomass calculation module for CanopyAI.

Computes below-ground biomass (BGB) and total biomass density from NASA GEDI
above-ground biomass density (AGBD in metric tonnes dry matter per hectare).

Scientific note:
The root-to-shoot ratios used here are initial configurable screening assumptions
derived from standard ecological literature (e.g., Mokany et al. 2006, IPCC 2019 Refinements).
They are intended for preliminary screening assessments and are configurable per biome.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

# Initial configurable screening assumptions for root-to-shoot ratios (R:S)
DEFAULT_ROOT_TO_SHOOT_RATIOS: dict[str, float] = {
    "Tropical Moist Broadleaf": 0.21,
    "Temperate Broadleaf": 0.26,
    "Boreal Coniferous": 0.24,
    "Other": 0.23,
}

# Fallback ratio when forest type is unrecognized
_DEFAULT_FALLBACK_RATIO: float = 0.23


def _normalize_type_key(forest_type: str) -> str:
    """Normalize a forest type name for flexible case-insensitive matching."""
    return "".join(c.lower() for c in forest_type if c.isalnum())


def _validate_non_negative_finite(value: float, name: str) -> float:
    """Validate that a numeric value is non-negative and finite."""
    if value is None:
        raise TypeError(f"{name} cannot be None.")
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a numeric value, got {type(value).__name__}.")
    if math.isnan(value):
        raise ValueError(f"{name} cannot be NaN.")
    if math.isinf(value):
        raise ValueError(f"{name} cannot be infinite.")
    if value < 0.0:
        raise ValueError(f"{name} cannot be negative (got {value}).")
    return float(value)


def get_root_to_shoot_ratio(
    forest_type: str = "Other",
    custom_ratios: Mapping[str, float] | None = None,
) -> float:
    """Look up the root-to-shoot ratio for a given forest type.

    Args:
        forest_type: Forest biome or type name (e.g., 'Tropical Moist Broadleaf').
        custom_ratios: Optional mapping of forest type names to custom root-to-shoot ratios.

    Returns:
        Root-to-shoot ratio as float.
    """
    if forest_type is None:
        raise TypeError("forest_type cannot be None.")

    if not isinstance(forest_type, str):
        raise TypeError(f"forest_type must be a string, got {type(forest_type).__name__}.")

    active_ratios = custom_ratios if custom_ratios is not None else DEFAULT_ROOT_TO_SHOOT_RATIOS

    # Direct match
    if forest_type in active_ratios:
        return float(active_ratios[forest_type])

    # Normalized comparison (case-insensitive, ignoring spaces/underscores)
    normalized_input = _normalize_type_key(forest_type)
    for key, ratio in active_ratios.items():
        if _normalize_type_key(key) == normalized_input:
            return float(ratio)

    # Fallback to 'Other' if present in active_ratios, else default fallback constant
    for key, ratio in active_ratios.items():
        if _normalize_type_key(key) == "other":
            return float(ratio)

    return _DEFAULT_FALLBACK_RATIO


def calculate_below_ground_biomass(
    agb_t_per_ha: float,
    forest_type: str = "Other",
    custom_ratios: Mapping[str, float] | None = None,
) -> float:
    """Calculate below-ground biomass density (BGB) from above-ground biomass (AGB).

    Formula:
        BGB = AGB × root_to_shoot_ratio

    Args:
        agb_t_per_ha: Above-ground biomass density in tonnes dry matter per hectare (t/ha).
                      Must be non-negative.
        forest_type: Forest classification name for looking up root-to-shoot ratio.
        custom_ratios: Optional dictionary overriding the default screening ratios.

    Returns:
        Below-ground biomass density in t/ha (float).

    Raises:
        ValueError: If agb_t_per_ha is negative, NaN, or infinite.
        TypeError: If agb_t_per_ha or forest_type is None or of invalid type.
    """
    validated_agb = _validate_non_negative_finite(agb_t_per_ha, "agb_t_per_ha")
    ratio = get_root_to_shoot_ratio(forest_type, custom_ratios=custom_ratios)
    if ratio < 0:
        raise ValueError(f"Root-to-shoot ratio cannot be negative (got {ratio}).")

    bgb = validated_agb * ratio
    return float(bgb)


def calculate_total_biomass(
    agb_t_per_ha: float,
    bgb_t_per_ha: float,
) -> float:
    """Calculate total biomass density (Total Biomass = AGB + BGB).

    Args:
        agb_t_per_ha: Above-ground biomass density in tonnes dry matter per hectare (t/ha).
        bgb_t_per_ha: Below-ground biomass density in tonnes dry matter per hectare (t/ha).

    Returns:
        Total biomass density in t/ha (float).

    Raises:
        ValueError: If either biomass value is negative, NaN, or infinite.
        TypeError: If either value is None or not a numeric type.
    """
    validated_agb = _validate_non_negative_finite(agb_t_per_ha, "agb_t_per_ha")
    validated_bgb = _validate_non_negative_finite(bgb_t_per_ha, "bgb_t_per_ha")
    return float(validated_agb + validated_bgb)
