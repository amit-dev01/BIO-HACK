"""Unit tests for the geospatial module (app/utils/geo.py)."""

from typing import Any, cast

import pytest
from shapely.geometry import Polygon

from app.utils.geo import (
    MAX_SUPPORTED_AREA_HA,
    MIN_SUPPORTED_AREA_HA,
    calculate_area_ha,
    get_bounding_box,
    get_centroid,
    is_area_supported,
    parse_polygon,
    validate_polygon,
    validate_polygon_area,
)


@pytest.fixture
def amazon_forest_geojson():
    """Valid GeoJSON polygon in Amazon Basin (~12,293 ha)."""
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


@pytest.fixture
def amazon_forest_feature(amazon_forest_geojson):
    """Valid GeoJSON Feature wrapping polygon."""
    return {
        "type": "Feature",
        "geometry": amazon_forest_geojson,
        "properties": {"name": "Amazon Stand 1"},
    }


@pytest.fixture
def raw_coords_ring():
    """Raw closed coordinates ring."""
    return [
        [-60.0, -3.0],
        [-60.0, -2.9],
        [-59.9, -2.9],
        [-59.9, -3.0],
        [-60.0, -3.0],
    ]


class TestPolygonValidation:
    """Tests for validate_polygon."""

    def test_valid_geojson_polygon(self, amazon_forest_geojson):
        assert validate_polygon(amazon_forest_geojson) is True

    def test_valid_geojson_feature(self, amazon_forest_feature):
        assert validate_polygon(amazon_forest_feature) is True

    def test_valid_raw_coordinates_ring(self, raw_coords_ring):
        assert validate_polygon(raw_coords_ring) is True

    def test_valid_nested_coordinates(self, raw_coords_ring):
        assert validate_polygon([raw_coords_ring]) is True

    def test_valid_shapely_polygon(self, raw_coords_ring):
        poly = Polygon(raw_coords_ring)
        assert validate_polygon(poly) is True

    def test_unclosed_polygon_rejected(self):
        """Polygon where first and last coordinates do not match."""
        unclosed = [
            [-60.0, -3.0],
            [-60.0, -2.9],
            [-59.9, -2.9],
            [-59.9, -3.0],
        ]
        assert validate_polygon(unclosed) is False
        assert validate_polygon({"type": "Polygon", "coordinates": [unclosed]}) is False

    def test_self_intersecting_bowtie_rejected(self):
        """Self-intersecting bowtie polygon."""
        bowtie = [
            [0.0, 0.0],
            [2.0, 2.0],
            [2.0, 0.0],
            [0.0, 2.0],
            [0.0, 0.0],
        ]
        assert validate_polygon(bowtie) is False
        assert validate_polygon({"type": "Polygon", "coordinates": [bowtie]}) is False

    def test_out_of_bounds_longitude_rejected(self):
        """Coordinates with longitude outside [-180, 180]."""
        invalid_lon = [
            [-185.0, 0.0],
            [-185.0, 1.0],
            [-184.0, 1.0],
            [-184.0, 0.0],
            [-185.0, 0.0],
        ]
        assert validate_polygon(invalid_lon) is False

    def test_out_of_bounds_latitude_rejected(self):
        """Coordinates with latitude outside [-90, 90]."""
        invalid_lat = [
            [0.0, 95.0],
            [0.0, 96.0],
            [1.0, 96.0],
            [1.0, 95.0],
            [0.0, 95.0],
        ]
        assert validate_polygon(invalid_lat) is False

    def test_degenerate_polygon_insufficient_points(self):
        """Fewer than 4 coordinates or fewer than 3 distinct points."""
        line = [[0.0, 0.0], [0.0, 1.0], [0.0, 0.0]]
        assert validate_polygon(line) is False

        same_points = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        assert validate_polygon(same_points) is False

    def test_missing_and_invalid_types(self):
        assert validate_polygon(None) is False
        assert validate_polygon([]) is False
        assert validate_polygon({}) is False
        assert validate_polygon("not a polygon") is False
        assert validate_polygon({"type": "Point", "coordinates": [0, 0]}) is False
        assert validate_polygon({"type": "Polygon", "coordinates": []}) is False
        assert validate_polygon({"type": "Polygon", "coordinates": [[[-60, -3], [-60, -2.9], [-59.9, -2.9]]]}) is False

    def test_coordinates_with_nan_inf_or_invalid_elements(self):
        nan_poly = [[0.0, 0.0], [float("nan"), 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
        assert validate_polygon(nan_poly) is False

        inf_poly = [[0.0, 0.0], [float("inf"), 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
        assert validate_polygon(inf_poly) is False

        short_coord = [[0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0]]
        assert validate_polygon(short_coord) is False

        string_coord = [["a", "b"], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], ["a", "b"]]
        assert validate_polygon(string_coord) is False

    def test_invalid_interior_holes(self):
        """Exterior is valid, but interior hole is unclosed or invalid."""
        outer = [[0.0, 0.0], [0.0, 2.0], [2.0, 2.0], [2.0, 0.0], [0.0, 0.0]]
        # Unclosed hole
        unclosed_hole = [[0.5, 0.5], [0.5, 1.5], [1.5, 1.5], [1.5, 0.5]]
        assert validate_polygon([outer, unclosed_hole]) is False

        # Self-intersecting bowtie hole
        bowtie_hole = [[0.5, 0.5], [1.5, 1.5], [1.5, 0.5], [0.5, 1.5], [0.5, 0.5]]
        assert validate_polygon([outer, bowtie_hole]) is False

    def test_parse_polygon_errors(self):
        with pytest.raises(TypeError, match="cannot be None"):
            parse_polygon(None)

        with pytest.raises(ValueError, match="Could not extract"):
            parse_polygon("not valid")

        with pytest.raises(ValueError, match="Invalid polygon"):
            parse_polygon([[0, 0], [1, 1], [0, 0]])


class TestAreaCalculation:
    """Tests for geodesic area calculation on WGS84 ellipsoid."""

    def test_area_calculation_accuracy(self, amazon_forest_geojson):
        area_ha = calculate_area_ha(amazon_forest_geojson)
        # Expected area for 0.1 x 0.1 degree box near equator is ~12,293 hectares
        assert 12_000.0 < area_ha < 12_500.0
        assert isinstance(area_ha, float)

    def test_area_with_interior_hole(self):
        """Polygon with an interior hole should have net area = exterior - hole."""
        outer = [
            [0.0, 0.0],
            [0.0, 0.2],
            [0.2, 0.2],
            [0.2, 0.0],
            [0.0, 0.0],
        ]
        hole = [
            [0.05, 0.05],
            [0.05, 0.15],
            [0.15, 0.15],
            [0.15, 0.05],
            [0.05, 0.05],
        ]
        solid_poly = {"type": "Polygon", "coordinates": [outer]}
        donut_poly = {"type": "Polygon", "coordinates": [outer, hole]}

        solid_area = calculate_area_ha(solid_poly)
        donut_area = calculate_area_ha(donut_poly)

        assert donut_area < solid_area
        assert donut_area > 0.0
        # The hole is 1/4 the linear dimensions of the outer square, so ~1/4 area
        assert abs(donut_area - (solid_area * 0.75)) < (solid_area * 0.05)

    def test_calculate_area_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            calculate_area_ha([[0, 0], [1, 1], [0, 0]])

    def test_calculate_area_none_raises_type_error(self):
        with pytest.raises(TypeError):
            calculate_area_ha(None)


class TestAreaLimits:
    """Tests for platform operational area boundaries (10 to 100,000 ha)."""

    def test_limits_constants(self):
        assert MIN_SUPPORTED_AREA_HA == 10.0
        assert MAX_SUPPORTED_AREA_HA == 100_000.0

    def test_is_area_supported(self):
        assert is_area_supported(9.9) is False
        assert is_area_supported(10.0) is True
        assert is_area_supported(50_000.0) is True
        assert is_area_supported(100_000.0) is True
        assert is_area_supported(100_000.1) is False
        assert is_area_supported(cast(Any, None)) is False
        assert is_area_supported(float("nan")) is False

    def test_validate_polygon_area_flag(self):
        # A tiny polygon (~0.01 ha)
        tiny_box = [
            [0.0, 0.0],
            [0.0, 0.001],
            [0.001, 0.001],
            [0.001, 0.0],
            [0.0, 0.0],
        ]
        # Geometry is valid
        assert validate_polygon(tiny_box) is True
        # Area is below minimum (10 ha)
        assert validate_polygon(tiny_box, check_area_limits=True) is False
        assert validate_polygon_area(tiny_box) is False


class TestCentroidAndBoundingBox:
    """Tests for get_centroid and get_bounding_box."""

    def test_get_centroid(self, amazon_forest_geojson):
        lon, lat = get_centroid(amazon_forest_geojson)
        assert isinstance(lon, float)
        assert isinstance(lat, float)
        assert pytest.approx(lon, abs=1e-4) == -59.95
        assert pytest.approx(lat, abs=1e-4) == -2.95

    def test_get_bounding_box(self, amazon_forest_geojson):
        bbox = get_bounding_box(amazon_forest_geojson)
        assert len(bbox) == 4
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon == -60.0
        assert min_lat == -3.0
        assert max_lon == -59.9
        assert max_lat == -2.9

    def test_invalid_polygon_raises(self):
        with pytest.raises(ValueError):
            get_centroid([[0, 0], [1, 1]])
        with pytest.raises(ValueError):
            get_bounding_box([[0, 0], [1, 1]])
