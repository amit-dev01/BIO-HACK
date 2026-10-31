"""Unit tests for Dynamic World canopy cover estimation (app/core/earth_engine.py).

Covers Phase 3 Canopy Cover Requirements:
1. Canopy cover for a dense tropical forest (expect > 80%)
2. Canopy cover for a sparse savanna (expect 20-40%)
3. Canopy cover for a non-forest area (expect < 10%)
4. Missing Dynamic World data (empty collection, zero pixels, missing stats)
5. Service failure and timeout handling
6. Dynamic and explicit year selection
7. Geometry validation
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.earth_engine import (
    DYNAMIC_WORLD_COLLECTION,
    get_canopy_cover,
)


@pytest.fixture
def amazon_polygon_dict():
    """Valid GeoJSON polygon dictionary in the Amazon basin."""
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
def savanna_polygon_dict():
    """Valid GeoJSON polygon dictionary in the Cerrado savanna."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-47.9, -15.8],
                [-47.9, -15.7],
                [-47.8, -15.7],
                [-47.8, -15.8],
                [-47.9, -15.8],
            ]
        ],
    }


@pytest.fixture
def urban_polygon_dict():
    """Valid GeoJSON polygon dictionary in an urban / non-forest region."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-46.65, -23.55],
                [-46.65, -23.54],
                [-46.64, -23.54],
                [-46.64, -23.55],
                [-46.65, -23.55],
            ]
        ],
    }


class TestCanopyCoverDetection:
    """Tests covering Google Dynamic World 10m canopy cover extraction."""

    def test_canopy_cover_dense_tropical_forest(self, amazon_polygon_dict):
        """Dense tropical forest yields high canopy cover (> 80%)."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 24

            mock_labels = MagicMock()
            mock_coll.select.return_value = mock_labels
            mock_mode = MagicMock()
            mock_labels.reduce.return_value = mock_mode
            mock_tree_binary = MagicMock()
            mock_mode.eq.return_value.rename.return_value = mock_tree_binary

            # Mean of binary mask across polygon = 0.874 (87.4% canopy cover)
            mock_tree_binary.reduceRegion.return_value.getInfo.return_value = {
                "trees_mean": 0.8742,
                "trees_count": 12500,
            }

            result = get_canopy_cover(amazon_polygon_dict)

            assert result["canopy_data_available"] is True
            assert result["canopy_pixel_count"] == 12500
            assert result["canopy_cover_pct"] == 87.4
            assert result["canopy_cover_pct"] > 80.0
            mock_ic.assert_called_with(DYNAMIC_WORLD_COLLECTION)

    def test_canopy_cover_sparse_savanna(self, savanna_polygon_dict):
        """Sparse savanna / woodland yields moderate canopy cover (expect 20-40%)."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 18

            mock_labels = MagicMock()
            mock_coll.select.return_value = mock_labels
            mock_mode = MagicMock()
            mock_labels.reduce.return_value = mock_mode
            mock_tree_binary = MagicMock()
            mock_mode.eq.return_value.rename.return_value = mock_tree_binary

            # Mean of binary mask = 0.285 (28.5% canopy cover)
            mock_tree_binary.reduceRegion.return_value.getInfo.return_value = {
                "trees_mean": 0.2854,
                "trees_count": 9400,
            }

            result = get_canopy_cover(savanna_polygon_dict)

            assert result["canopy_data_available"] is True
            assert result["canopy_pixel_count"] == 9400
            assert result["canopy_cover_pct"] == 28.5
            assert 20.0 <= result["canopy_cover_pct"] <= 40.0

    def test_canopy_cover_non_forest(self, urban_polygon_dict):
        """Non-forest or built-up area yields very low canopy cover (expect < 10%)."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 12

            mock_labels = MagicMock()
            mock_coll.select.return_value = mock_labels
            mock_mode = MagicMock()
            mock_labels.reduce.return_value = mock_mode
            mock_tree_binary = MagicMock()
            mock_mode.eq.return_value.rename.return_value = mock_tree_binary

            # Mean of binary mask = 0.042 (4.2% canopy cover)
            mock_tree_binary.reduceRegion.return_value.getInfo.return_value = {
                "trees_mean": 0.0421,
                "trees_count": 8100,
            }

            result = get_canopy_cover(urban_polygon_dict)

            assert result["canopy_data_available"] is True
            assert result["canopy_pixel_count"] == 8100
            assert result["canopy_cover_pct"] == 4.2
            assert result["canopy_cover_pct"] < 10.0

    def test_missing_dynamic_world_data_empty_collection(self, amazon_polygon_dict):
        """When Dynamic World collection is empty, returns null and availability False."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic:

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 0

            result = get_canopy_cover(amazon_polygon_dict)

            assert result["canopy_data_available"] is False
            assert result["canopy_cover_pct"] is None
            assert result["canopy_pixel_count"] == 0

    def test_missing_dynamic_world_data_empty_stats(self, amazon_polygon_dict):
        """When reduceRegion returns None or zero count, returns null canopy cover."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 5

            mock_labels = MagicMock()
            mock_coll.select.return_value = mock_labels
            mock_mode = MagicMock()
            mock_labels.reduce.return_value = mock_mode
            mock_tree_binary = MagicMock()
            mock_mode.eq.return_value.rename.return_value = mock_tree_binary
            mock_tree_binary.reduceRegion.return_value.getInfo.return_value = None

            result = get_canopy_cover(amazon_polygon_dict)

            assert result["canopy_data_available"] is False
            assert result["canopy_cover_pct"] is None
            assert result["canopy_pixel_count"] == 0

    def test_canopy_cover_service_failure_safe_fallback(self, amazon_polygon_dict):
        """Earth Engine timeouts return null indicators without crashing the pipeline."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=RuntimeError("Dynamic World timeout")):

            result = get_canopy_cover(amazon_polygon_dict)

            assert result["canopy_data_available"] is False
            assert result["canopy_cover_pct"] is None
            assert result["canopy_pixel_count"] == 0

    def test_canopy_cover_service_failure_raise_on_error(self, amazon_polygon_dict):
        """When raise_on_error=True, re-raises underlying Earth Engine exception."""
        with (
            patch("app.core.earth_engine._ensure_initialized"),
            patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=RuntimeError("EE timeout")),
            pytest.raises(RuntimeError, match="EE timeout"),
        ):
            get_canopy_cover(amazon_polygon_dict, raise_on_error=True)

    def test_canopy_cover_explicit_year_selection(self, amazon_polygon_dict):
        """Explicit year argument filters between year-01-01 and year+1-01-01."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 10

            mock_labels = MagicMock()
            mock_coll.select.return_value = mock_labels
            mock_mode = MagicMock()
            mock_labels.reduce.return_value = mock_mode
            mock_tree_binary = MagicMock()
            mock_mode.eq.return_value.rename.return_value = mock_tree_binary
            mock_tree_binary.reduceRegion.return_value.getInfo.return_value = {
                "trees_mean": 0.72,
                "trees_count": 5000,
            }

            result = get_canopy_cover(amazon_polygon_dict, year=2024)

            mock_coll.filterDate.assert_called_once_with("2024-01-01", "2025-01-01")
            assert result["canopy_cover_pct"] == 72.0

    def test_canopy_cover_invalid_polygon_raises_value_error(self):
        """Unclosed polygon raises ValueError."""
        unclosed = {
            "type": "Polygon",
            "coordinates": [[[-60.0, -3.0], [-60.0, -2.9], [-59.9, -2.9], [-59.9, -3.0]]],
        }
        with pytest.raises(ValueError, match="Invalid polygon"):
            get_canopy_cover(unclosed)

    def test_canopy_cover_none_polygon_raises_type_error(self):
        """None polygon raises TypeError."""
        with pytest.raises(TypeError, match="cannot be None"):
            get_canopy_cover(None)

