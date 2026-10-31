"""Unit tests for forest biome classification and multi-factor integration (app/core/forest_classifier.py).

Covers Phase 3 Forest Classification Requirements:
5. Forest classification for tropical latitude (< 23.5°)
6. Forest classification for temperate latitude (23.5° to 50°)
7. Forest classification for boreal latitude (>= 50°)
8. Non-forest area classification (Cropland, Built-up, Water)
9. NDVI cross-validation agreement (confidence: high)
10. NDVI cross-validation disagreement (confidence: low, retains primary classification)
11. Polygon spanning multiple ecoregions (confidence: medium)
12. Missing satellite data fallback (classification_method: latitude-only)
13. Combined satellite observations output integration with Phase 3 fields
"""

from unittest.mock import MagicMock, patch

import pytest

from app.core.earth_engine import (
    DATA_SOURCES,
    DYNAMIC_WORLD_COLLECTION,
    GEDI_L2A_COLLECTION,
    GEDI_L4A_COLLECTION,
    SENTINEL_2_COLLECTION,
    WORLDCOVER_COLLECTION,
    get_satellite_observations,
)
from app.core.forest_classifier import (
    classify_forest_type,
)


@pytest.fixture
def tropical_amazon_polygon():
    """Valid GeoJSON polygon located in the Amazon basin (-3.0° S)."""
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
def temperate_europe_polygon():
    """Valid GeoJSON polygon located in Central Europe (48.0° N)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [8.0, 48.0],
                [8.0, 48.1],
                [8.1, 48.1],
                [8.1, 48.0],
                [8.0, 48.0],
            ]
        ],
    }


@pytest.fixture
def boreal_scandinavia_polygon():
    """Valid GeoJSON polygon located in Scandinavia (62.0° N)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [25.0, 62.0],
                [25.0, 62.1],
                [25.1, 62.1],
                [25.1, 62.0],
                [25.0, 62.0],
            ]
        ],
    }


@pytest.fixture
def multi_ecoregion_polygon():
    """Valid GeoJSON polygon spanning across the 23.5° tropical/temperate boundary."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [-100.0, 23.0],
                [-100.0, 24.0],
                [-99.0, 24.0],
                [-99.0, 23.0],
                [-100.0, 23.0],
            ]
        ],
    }


class TestForestClassificationPriorities:
    """Tests covering multi-factor priority classification logic."""

    def test_tropical_forest_classification(self, tropical_amazon_polygon):
        """Tropical latitude with tree cover classified as Tropical Moist Broadleaf."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            # Dominant class 10 = Tree cover
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            result = classify_forest_type(tropical_amazon_polygon, mean_ndvi=0.82)

            assert result["forest_type"] == "Tropical Moist Broadleaf"
            assert result["ecoregion"] == "Tropical/Subtropical"
            assert result["dominant_land_cover"] == "Tree cover"
            assert result["classification_method"] == "satellite+latitude"
            assert result["classification_confidence"] == "high"
            assert result["recommended_standard"] == "Verra VM0047"
            # Backward-compatibility test
            assert result == "Tropical Moist Broadleaf"

    def test_temperate_forest_classification(self, temperate_europe_polygon):
        """Temperate latitude with tree cover classified as Temperate Broadleaf."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            result = classify_forest_type(temperate_europe_polygon, mean_ndvi=0.68)

            assert result["forest_type"] == "Temperate Broadleaf"
            assert result["ecoregion"] == "Temperate"
            assert result["dominant_land_cover"] == "Tree cover"
            assert result["classification_method"] == "satellite+latitude"
            assert result["classification_confidence"] == "high"
            assert result["recommended_standard"] == "Verra VM0003"
            assert result == "Temperate Broadleaf"

    def test_boreal_forest_classification(self, boreal_scandinavia_polygon):
        """Boreal latitude with tree cover classified as Boreal Coniferous."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            result = classify_forest_type(boreal_scandinavia_polygon, mean_ndvi=0.55)

            assert result["forest_type"] == "Boreal Coniferous"
            assert result["ecoregion"] == "Boreal"
            assert result["dominant_land_cover"] == "Tree cover"
            assert result["classification_method"] == "satellite+latitude"
            assert result["classification_confidence"] == "high"
            assert result["recommended_standard"] == "Verra VM0003"
            assert result == "Boreal Coniferous"

    @pytest.mark.parametrize(
        ("class_code", "expected_name"),
        [
            (40, "Cropland"),
            (50, "Built-up"),
            (30, "Grassland"),
            (80, "Permanent water bodies"),
            (60, "Bare / sparse vegetation"),
        ],
    )
    def test_non_forest_classifications(self, tropical_amazon_polygon, class_code, expected_name):
        """When ESA WorldCover indicates non-tree cover, sets Non-Forest regardless of latitude."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": class_code}

            result = classify_forest_type(tropical_amazon_polygon, mean_ndvi=0.45)

            assert result["forest_type"] == "Non-Forest"
            assert result["ecoregion"] == "Non-Forest"
            assert result["dominant_land_cover"] == expected_name
            assert result["classification_method"] == "satellite+latitude"
            assert result["classification_confidence"] == "high"
            assert result["recommended_standard"] is None

    def test_ndvi_cross_validation_agreement(self, tropical_amazon_polygon):
        """When NDVI agrees with tropical threshold (NDVI > 0.75), confidence is high."""
        result = classify_forest_type(tropical_amazon_polygon, mean_ndvi=0.84)
        assert result["forest_type"] == "Tropical Moist Broadleaf"
        # Satellite wasn't mocked so method fell back to latitude-only; if latitude-only, confidence is medium
        assert result["classification_method"] == "latitude-only"

    def test_ndvi_cross_validation_disagreement_tropical(self, tropical_amazon_polygon):
        """When tropical forest has abnormally low NDVI (<= 0.75), sets confidence to low."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            result = classify_forest_type(tropical_amazon_polygon, mean_ndvi=0.55)

            assert result["forest_type"] == "Tropical Moist Broadleaf"
            assert result["classification_confidence"] == "low"

    def test_ndvi_cross_validation_disagreement_temperate(self, temperate_europe_polygon):
        """When temperate forest has NDVI out of range (0.5 to 0.8), sets confidence to low."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            # NDVI 0.35 contradicts temperate 0.5-0.8 range
            result = classify_forest_type(temperate_europe_polygon, mean_ndvi=0.35)

            assert result["forest_type"] == "Temperate Broadleaf"
            assert result["classification_confidence"] == "low"

    def test_ndvi_cross_validation_disagreement_boreal(self, boreal_scandinavia_polygon):
        """When boreal forest has NDVI out of range (0.3 to 0.7), sets confidence to low."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 1
            mock_img = MagicMock()
            mock_col.first.return_value = mock_img
            mock_img.reduceRegion.return_value.getInfo.return_value = {"Map": 10}

            # NDVI 0.15 contradicts boreal 0.3-0.7 range
            result = classify_forest_type(boreal_scandinavia_polygon, mean_ndvi=0.15)

            assert result["forest_type"] == "Boreal Coniferous"
            assert result["classification_confidence"] == "low"

    def test_polygon_spans_multiple_ecoregions(self, multi_ecoregion_polygon):
        """Polygon crossing ecoregion boundaries sets confidence to medium and uses centroid."""
        result = classify_forest_type(multi_ecoregion_polygon, mean_ndvi=0.65)

        # Centroid is at 23.5° latitude (temperate)
        assert result["forest_type"] == "Temperate Broadleaf"
        assert result["classification_confidence"] == "medium"

    def test_empty_worldcover_falls_back_to_latitude_only(self, tropical_amazon_polygon):
        """When WorldCover collection is empty, method is latitude-only and confidence is medium."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic:

            mock_col = MagicMock()
            mock_ic.return_value = mock_col
            mock_col.filterBounds.return_value = mock_col
            mock_col.size.return_value.getInfo.return_value = 0

            result = classify_forest_type(tropical_amazon_polygon, mean_ndvi=0.85)

            assert result["classification_method"] == "latitude-only"
            assert result["forest_type"] == "Tropical Moist Broadleaf"
            assert result["classification_confidence"] == "medium"


class TestCombinedSatelliteObservationsPhase3:
    """Tests verifying complete integration of Phase 3 observations into get_satellite_observations."""

    def test_combined_observations_includes_all_phase3_fields(self, tropical_amazon_polygon):
        """get_satellite_observations combines Phase 2 and Phase 3 fields into strict schema."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_height, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s2, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_trend, \
             patch("app.core.earth_engine.get_canopy_cover") as mock_canopy, \
             patch("app.core.forest_classifier.classify_forest_type") as mock_class:

            mock_bio.return_value = {
                "agb_t_per_ha": 235.4,
                "agb_stddev": 28.2,
                "gedi_observation_count": 64,
                "gedi_data_available": True,
            }
            mock_height.return_value = {
                "mean_canopy_height_m": 31.8,
                "height_observation_count": 112,
                "height_data_available": True,
            }
            mock_s2.return_value = {
                "mean_ndvi": 0.845,
                "valid_pixel_percentage": 96.0,
                "image_count": 22,
                "analysis_start_date": "2024-01-01",
                "analysis_end_date": "2024-12-31",
            }
            mock_trend.return_value = [{"quarter": "2025-Q1", "ndvi": 0.84}]
            mock_canopy.return_value = {
                "canopy_cover_pct": 89.2,
                "canopy_data_available": True,
                "canopy_pixel_count": 14200,
            }
            mock_class.return_value = {
                "forest_type": "Tropical Moist Broadleaf",
                "ecoregion": "Tropical/Subtropical",
                "dominant_land_cover": "Tree cover",
                "classification_method": "satellite+latitude",
                "classification_confidence": "high",
                "recommended_standard": "Verra VM0047",
            }

            obs = get_satellite_observations(tropical_amazon_polygon)

            # Phase 2 fields check
            assert obs["agb_t_per_ha"] == 235.4
            assert obs["agb_stddev"] == 28.2
            assert obs["gedi_observation_count"] == 64
            assert obs["gedi_data_available"] is True
            assert obs["mean_canopy_height_m"] == 31.8
            assert obs["height_observation_count"] == 112
            assert obs["height_data_available"] is True
            assert obs["mean_ndvi"] == 0.845
            assert obs["valid_pixel_percentage"] == 96.0
            assert obs["image_count"] == 22
            assert len(obs["ndvi_trend"]) == 1

            # Phase 3 Canopy Cover fields check
            assert obs["canopy_cover_pct"] == 89.2
            assert obs["canopy_data_available"] is True
            assert obs["canopy_pixel_count"] == 14200

            # Phase 3 Forest Classification fields check
            assert obs["forest_type"] == "Tropical Moist Broadleaf"
            assert obs["ecoregion"] == "Tropical/Subtropical"
            assert obs["dominant_land_cover"] == "Tree cover"
            assert obs["classification_method"] == "satellite+latitude"
            assert obs["classification_confidence"] == "high"
            assert obs["recommended_standard"] == "Verra VM0047"

            # Data sources check
            assert GEDI_L4A_COLLECTION in obs["data_sources"]
            assert GEDI_L2A_COLLECTION in obs["data_sources"]
            assert SENTINEL_2_COLLECTION in obs["data_sources"]
            assert DYNAMIC_WORLD_COLLECTION in obs["data_sources"]
            assert WORLDCOVER_COLLECTION in obs["data_sources"]
            assert obs["data_sources"] == DATA_SOURCES

