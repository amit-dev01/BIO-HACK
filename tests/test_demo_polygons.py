"""Unit tests verifying structural integrity, validity, and geospatial correctness of demo/demo_polygons.json.

Ensures the curated demo dataset for the hackathon meets all scientific and operational criteria:
- Exactly 13 polygons (10 global forest reference ecosystems + 3 edge cases)
- Valid GeoJSON Polygon geometry format in [longitude, latitude] order
- Geodesic area within operational bounds (100 to 5,000 hectares)
- Required metadata fields, reference citations, and plausible expected ranges
"""

import json
from pathlib import Path
from typing import Any

import pytest

from app.utils.geo import calculate_area_ha, get_centroid, validate_polygon

DEMO_FILE_PATH = Path(__file__).resolve().parent.parent / "demo" / "demo_polygons.json"


@pytest.fixture(scope="module")
def demo_polygons() -> list[dict[str, Any]]:
    """Load the demo polygons dataset from disk."""
    assert DEMO_FILE_PATH.exists(), f"Demo polygon file not found at {DEMO_FILE_PATH}"
    with open(DEMO_FILE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), "demo_polygons.json must contain a JSON array"
    return data


class TestDemoPolygonsDataset:
    """Test suite for the curated demo polygons dataset."""

    def test_polygon_count(self, demo_polygons: list[dict[str, Any]]):
        """Must contain exactly 13 polygons: 10 global forest benchmarks + 3 edge cases."""
        assert len(demo_polygons) == 13, f"Expected 13 demo polygons, got {len(demo_polygons)}"

    def test_required_metadata_fields(self, demo_polygons: list[dict[str, Any]]):
        """Every polygon record must have all required metadata fields."""
        required_keys = {
            "id",
            "name",
            "country",
            "ecosystem",
            "polygon",
            "expected_agb_range",
            "expected_canopy_cover_range",
            "expected_forest_type",
            "reference_source",
            "notes",
        }
        for item in demo_polygons:
            poly_id = item.get("id", "UNKNOWN")
            missing = required_keys - set(item.keys())
            assert not missing, f"Polygon '{poly_id}' missing keys: {missing}"
            assert isinstance(item["id"], str) and len(item["id"]) > 0
            assert isinstance(item["name"], str) and len(item["name"]) > 0
            assert isinstance(item["country"], str) and len(item["country"]) > 0
            assert isinstance(item["reference_source"], str) and len(item["reference_source"]) > 0

    def test_geojson_polygon_geometry_validity(self, demo_polygons: list[dict[str, Any]]):
        """All polygons must be valid GeoJSON geometries under WGS84."""
        for item in demo_polygons:
            poly_id = item["id"]
            geom = item["polygon"]
            assert isinstance(geom, dict), f"'{poly_id}' geometry must be a dict"
            assert geom.get("type") == "Polygon", f"'{poly_id}' type must be 'Polygon'"

            coords = geom.get("coordinates")
            assert isinstance(coords, list) and len(coords) >= 1, f"'{poly_id}' coordinates invalid"
            ring = coords[0]
            assert len(ring) >= 4, f"'{poly_id}' exterior ring must have >= 4 coordinates"
            assert ring[0] == ring[-1], f"'{poly_id}' exterior ring must be closed (first == last)"

            # Coordinates must be valid [lon, lat] pairs within [-180, 180] and [-90, 90]
            for pt in ring:
                assert len(pt) == 2, f"Coordinate pair {pt} must have length 2"
                lon, lat = pt[0], pt[1]
                assert -180.0 <= lon <= 180.0, f"Longitude {lon} out of range in '{poly_id}'"
                assert -90.0 <= lat <= 90.0, f"Latitude {lat} out of range in '{poly_id}'"

            # Validate using CanopyAI geo validation function
            assert validate_polygon(geom), f"'{poly_id}' failed geo.validate_polygon"

    def test_polygon_area_bounds(self, demo_polygons: list[dict[str, Any]]):
        """Every demo polygon must have a geodesic area between 100 and 5,000 hectares."""
        for item in demo_polygons:
            poly_id = item["id"]
            geom = item["polygon"]
            area_ha = calculate_area_ha(geom)
            assert 100.0 <= area_ha <= 5000.0, (
                f"Polygon '{poly_id}' area {area_ha:.2f} ha is outside [100, 5000] ha limit."
            )

    def test_expected_ranges_plausibility(self, demo_polygons: list[dict[str, Any]]):
        """Expected AGB and canopy cover ranges must be valid non-negative intervals."""
        for item in demo_polygons:
            poly_id = item["id"]
            agb_range = item["expected_agb_range"]
            canopy_range = item["expected_canopy_cover_range"]

            assert len(agb_range) == 2, f"'{poly_id}' expected_agb_range must have 2 numbers"
            assert 0.0 <= agb_range[0] <= agb_range[1] <= 1000.0, (
                f"'{poly_id}' AGB range {agb_range} invalid"
            )

            assert len(canopy_range) == 2, f"'{poly_id}' expected_canopy_cover_range must have 2 numbers"
            assert 0.0 <= canopy_range[0] <= canopy_range[1] <= 100.0, (
                f"'{poly_id}' canopy cover range {canopy_range} invalid"
            )

    def test_edge_case_polygons_represented(self, demo_polygons: list[dict[str, Any]]):
        """Must include Sahara Desert, Pacific Ocean, and Amazon Deforested patch."""
        ids = {p["id"] for p in demo_polygons}
        assert "sahara_desert_11" in ids, "Missing Sahara Desert edge case"
        assert "pacific_ocean_12" in ids, "Missing Pacific Ocean edge case"
        assert "deforested_amazon_13" in ids, "Missing Deforested Amazon patch edge case"

        desert = next(p for p in demo_polygons if p["id"] == "sahara_desert_11")
        assert desert["expected_forest_type"] == "Non-Forest"
        assert desert["expected_agb_range"][1] <= 15.0

        ocean = next(p for p in demo_polygons if p["id"] == "pacific_ocean_12")
        assert ocean["expected_forest_type"] == "Non-Forest"
        assert ocean["expected_agb_range"] == [0.0, 0.0]

    def test_centroids_align_with_target_ecoregions(self, demo_polygons: list[dict[str, Any]]):
        """Centroid coordinates must be located in correct hemispheres and geographic zones."""
        for item in demo_polygons:
            poly_id = item["id"]
            lon, lat = get_centroid(item["polygon"])

            if "amazon" in poly_id:
                assert -75.0 <= lon <= -45.0 and -15.0 <= lat <= 5.0
            elif "congo" in poly_id:
                assert 15.0 <= lon <= 30.0 and -5.0 <= lat <= 5.0
            elif "boreal_finland" in poly_id:
                assert 20.0 <= lon <= 35.0 and 60.0 <= lat <= 70.0
            elif "redwood" in poly_id:
                assert -125.0 <= lon <= -120.0 and 40.0 <= lat <= 45.0
            elif "sundarbans" in poly_id:
                assert 85.0 <= lon <= 95.0 and 20.0 <= lat <= 25.0
