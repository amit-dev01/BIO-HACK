"""Automated reference accuracy validation test suite.

Validates that CanopyAI estimates for all curated demonstration polygons
fall within published scientific baseline ranges:
1. Above-ground biomass density (AGB) is within ±40% screening tolerance of published midpoint.
2. Canopy cover percentage is within ±20% absolute tolerance of expected midpoint.
3. Forest type classification matches expected ecological biome.
4. Confidence score is at least 50/100 for all well-studied global forest benchmark sites.

Marked with:
  @pytest.mark.slow
  @pytest.mark.integration
"""

import json
from pathlib import Path
from typing import Any

import pytest

from demo.demo_runner import analyze_demo_polygon

DEMO_FILE = Path(__file__).resolve().parent.parent / "demo" / "demo_polygons.json"


@pytest.fixture(scope="module")
def demo_dataset() -> list[dict[str, Any]]:
    """Load demo polygons for accuracy verification."""
    assert DEMO_FILE.exists(), f"Demo file missing at {DEMO_FILE}"
    with open(DEMO_FILE, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def analyzed_results(demo_dataset: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Run pipeline analysis for all demo polygons in test mode."""
    results: dict[str, dict[str, Any]] = {}
    for item in demo_dataset:
        # Use calibrated reference mode for deterministic accuracy test execution
        res = analyze_demo_polygon(item, is_live_gee=False)
        results[item["id"]] = res
    return results


@pytest.mark.slow
@pytest.mark.integration
class TestReferenceAccuracy:
    """Scientific verification against published reference literature."""

    def test_forest_biomass_within_tolerance(
        self,
        demo_dataset: list[dict[str, Any]],
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """AGB estimate must fall within ±40% tolerance of the expected published midpoint."""
        for item in demo_dataset:
            poly_id = item["id"]
            if poly_id in ("sahara_desert_11", "pacific_ocean_12"):
                continue  # Non-forest zero biomass evaluated separately

            exp_range = item["expected_agb_range"]
            exp_mid = (exp_range[0] + exp_range[1]) / 2.0
            actual_agb = analyzed_results[poly_id]["canopyai_agb_t_per_ha"]

            lower_bound = exp_mid * 0.60  # -40%
            upper_bound = exp_mid * 1.40  # +40%

            assert lower_bound <= actual_agb <= upper_bound, (
                f"[{poly_id}] AGB {actual_agb} outside ±40% tolerance [{lower_bound:.1f}, {upper_bound:.1f}] "
                f"(Midpoint: {exp_mid:.1f})"
            )

    def test_forest_canopy_cover_within_tolerance(
        self,
        demo_dataset: list[dict[str, Any]],
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """Canopy cover must be within ±20% absolute tolerance of expected midpoint."""
        for item in demo_dataset:
            poly_id = item["id"]
            if poly_id in ("sahara_desert_11", "pacific_ocean_12"):
                continue

            exp_range = item["expected_canopy_cover_range"]
            exp_mid = (exp_range[0] + exp_range[1]) / 2.0
            actual_canopy = analyzed_results[poly_id]["canopyai_canopy_cover_pct"]

            lower_bound = max(0.0, exp_mid - 20.0)
            upper_bound = min(100.0, exp_mid + 20.0)

            assert lower_bound <= actual_canopy <= upper_bound, (
                f"[{poly_id}] Canopy cover {actual_canopy}% outside ±20% range "
                f"[{lower_bound:.1f}%, {upper_bound:.1f}%]"
            )

    def test_forest_type_classification_matches_expected(
        self,
        demo_dataset: list[dict[str, Any]],
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """Forest type classification must match expected classification."""
        for item in demo_dataset:
            poly_id = item["id"]
            expected_type = item["expected_forest_type"]
            actual_type = analyzed_results[poly_id]["canopyai_forest_type"]

            assert actual_type == expected_type, (
                f"[{poly_id}] Forest type '{actual_type}' != expected '{expected_type}'"
            )

    def test_well_studied_forests_confidence_score(
        self,
        demo_dataset: list[dict[str, Any]],
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """Well-studied reference forests must achieve a confidence score of at least 50/100."""
        # Top 10 primary forest reference sites
        forest_ids = [
            "amazon_01",
            "congo_02",
            "borneo_03",
            "black_forest_04",
            "redwood_05",
            "boreal_finland_06",
            "siberian_taiga_07",
            "sundarbans_08",
            "western_ghats_09",
            "yasuni_10",
        ]
        for poly_id in forest_ids:
            score = analyzed_results[poly_id]["confidence_score"]
            assert score >= 50, (
                f"[{poly_id}] Confidence score {score} is lower than 50 threshold for reference site."
            )

    def test_non_forest_edge_cases(
        self,
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """Sahara desert and Pacific Ocean return 0 biomass, 0 carbon, and 0 confidence score."""
        desert = analyzed_results["sahara_desert_11"]
        assert desert["canopyai_agb_t_per_ha"] == 0.0
        assert desert["total_co2e_tonnes"] == 0.0
        assert desert["confidence_score"] == 0
        assert desert["canopyai_forest_type"] == "Non-Forest"

        ocean = analyzed_results["pacific_ocean_12"]
        assert ocean["canopyai_agb_t_per_ha"] == 0.0
        assert ocean["total_co2e_tonnes"] == 0.0
        assert ocean["confidence_score"] == 0
        assert ocean["canopyai_forest_type"] == "Non-Forest"

    def test_deforested_amazon_patch(
        self,
        analyzed_results: dict[str, dict[str, Any]],
    ):
        """Deforested Amazon patch demonstrates low biomass and deforestation warnings."""
        degraded = analyzed_results["deforested_amazon_13"]
        assert 10.0 <= degraded["canopyai_agb_t_per_ha"] <= 80.0
        assert degraded["confidence_score"] < 80  # Downgraded confidence
        assert any("loss" in w.lower() or "deforestation" in w.lower() for w in degraded["data_warnings"])
