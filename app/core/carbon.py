"""Carbon and CO2 equivalent calculation module for CanopyAI.

Scientific Basis:
- IPCC default carbon fraction: 0.47 (47% of dry woody biomass is carbon).
- Molecular weight ratio: CO2 (44) to Carbon (12) = 44 / 12 ≈ 3.6667.

IMPORTANT SCIENTIFIC DISCLAIMER:
- These calculations estimate EXISTING STANDING CARBON STOCKS in forest biomass.
- Existing carbon stock DOES NOT EQUAL carbon credits, additionality, or annual sequestration rates.
- Do NOT use these values as carbon credit revenue projections. Carbon crediting requires
  rigorous baseline modeling, permanence buffers, leakage assessment, and accredited registry verification.
"""

from __future__ import annotations

import math

# IPCC Tier 1 default carbon fraction for dry matter in woody biomass
CARBON_FRACTION: float = 0.47

# Stoichiometric conversion ratio from Carbon (C) to Carbon Dioxide (CO2): 44 / 12
CO2_TO_CARBON_RATIO: float = 44.0 / 12.0


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


def calculate_carbon_stock(
    total_biomass_t_per_ha: float,
) -> float:
    """Calculate existing carbon stock density from total biomass density.

    Formula:
        Carbon Stock = Total Biomass × 0.47

    Args:
        total_biomass_t_per_ha: Total biomass density in tonnes dry matter per hectare (t/ha).
                                Must be non-negative.

    Returns:
        Carbon stock density in tonnes Carbon per hectare (t C/ha) as float.

    Raises:
        ValueError: If total_biomass_t_per_ha is negative, NaN, or infinite.
        TypeError: If total_biomass_t_per_ha is None or non-numeric.
    """
    biomass = _validate_non_negative_finite(total_biomass_t_per_ha, "total_biomass_t_per_ha")
    return float(biomass * CARBON_FRACTION)


def calculate_co2_equivalent(
    carbon_t_per_ha: float,
) -> float:
    """Convert carbon stock density to carbon dioxide equivalent (CO2e) density.

    Formula:
        CO2 Equivalent = Carbon Stock × (44 / 12)

    Args:
        carbon_t_per_ha: Carbon stock density in tonnes Carbon per hectare (t C/ha).
                         Must be non-negative.

    Returns:
        Carbon dioxide equivalent density in tonnes CO2e per hectare (t CO2e/ha) as float.

    Raises:
        ValueError: If carbon_t_per_ha is negative, NaN, or infinite.
        TypeError: If carbon_t_per_ha is None or non-numeric.
    """
    carbon = _validate_non_negative_finite(carbon_t_per_ha, "carbon_t_per_ha")
    return float(carbon * CO2_TO_CARBON_RATIO)


def calculate_total_co2(
    co2e_t_per_ha: float,
    area_ha: float,
) -> float:
    """Calculate the total existing standing CO2 equivalent for a forest area.

    Formula:
        Total CO2e = CO2e per hectare × Area

    Args:
        co2e_t_per_ha: CO2 equivalent density in tonnes CO2e per hectare (t CO2e/ha).
        area_ha: Forest polygon area in hectares (ha).

    Returns:
        Total standing CO2 equivalent in metric tonnes (t CO2e) as float.

    Raises:
        ValueError: If co2e_t_per_ha or area_ha is negative, NaN, or infinite.
        TypeError: If either value is None or non-numeric.
    """
    co2e = _validate_non_negative_finite(co2e_t_per_ha, "co2e_t_per_ha")
    area = _validate_non_negative_finite(area_ha, "area_ha")
    return float(co2e * area)
