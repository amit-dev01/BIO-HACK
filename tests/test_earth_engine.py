"""Comprehensive unit tests for the Earth Engine satellite data processing module.

Tests cover all 10 required operational categories:
1. Earth Engine initialization
2. Valid polygon input
3. NASA GEDI biomass extraction
4. Missing GEDI observations
5. NASA GEDI canopy height extraction
6. ESA Sentinel-2 NDVI calculation
7. Missing cloud-free imagery
8. Quarterly NDVI trend generation (20 quarters, 5 complete calendar years)
9. Empty satellite datasets
10. Earth Engine service failures and timeouts
11. Forest type classification integration
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from shapely.geometry import Polygon

from app.core.earth_engine import (
    DATA_SOURCES,
    GEDI_L2A_COLLECTION,
    GEDI_L4A_COLLECTION,
    SENTINEL_2_COLLECTION,
    get_gedi_biomass,
    get_gedi_canopy_height,
    get_ndvi_trend,
    get_recent_complete_years,
    get_satellite_observations,
    get_sentinel_ndvi,
    initialize_earth_engine,
    polygon_to_ee_geometry,
    reset_earth_engine,
)
from app.core.forest_classifier import classify_forest_type
from app.models.schemas import GeoJSONPolygon


@pytest.fixture(autouse=True)
def clean_ee_state():
    """Ensure clean initialization state before and after each test."""
    reset_earth_engine()
    yield
    reset_earth_engine()


@pytest.fixture
def amazon_polygon_dict():
    """Valid GeoJSON polygon dictionary in the Amazon basin (~12,293 ha)."""
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
def amazon_feature_dict(amazon_polygon_dict):
    """Valid GeoJSON Feature wrapping polygon."""
    return {
        "type": "Feature",
        "geometry": amazon_polygon_dict,
        "properties": {"name": "Amazon Stand 1"},
    }


@pytest.fixture
def amazon_shapely_poly():
    """Valid Shapely polygon in the Amazon basin."""
    return Polygon([[-60.0, -3.0], [-60.0, -2.9], [-59.9, -2.9], [-59.9, -3.0], [-60.0, -3.0]])


@pytest.fixture
def amazon_pydantic_poly(amazon_polygon_dict):
    """Valid Pydantic GeoJSONPolygon model."""
    return GeoJSONPolygon(**amazon_polygon_dict)


# ============================================================================
# 1. Earth Engine Initialization Tests
# ============================================================================


class TestEarthEngineInitialization:
    """Tests covering Google Earth Engine authentication, initialization, and configuration."""

    def test_init_missing_credentials_raises_error(self, monkeypatch):
        """When credentials environment variables are missing, raises descriptive RuntimeError."""
        monkeypatch.delenv("GEE_SERVICE_ACCOUNT_EMAIL", raising=False)
        monkeypatch.delenv("GEE_PRIVATE_KEY_PATH", raising=False)
        monkeypatch.delenv("GEE_PROJECT_ID", raising=False)
        monkeypatch.delenv("EARTH_ENGINE_SERVICE_ACCOUNT", raising=False)
        monkeypatch.delenv("EARTH_ENGINE_PRIVATE_KEY", raising=False)

        with pytest.raises(RuntimeError, match="Google Earth Engine credentials missing"):
            initialize_earth_engine()

    def test_init_missing_partial_credentials_raises_error(self, monkeypatch):
        """When only email is set but key and project are missing, raises RuntimeError."""
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.iam.gserviceaccount.com")
        monkeypatch.delenv("GEE_PRIVATE_KEY_PATH", raising=False)
        monkeypatch.delenv("GEE_PROJECT_ID", raising=False)

        with pytest.raises(RuntimeError, match="GEE_PRIVATE_KEY_PATH"):
            initialize_earth_engine()

    def test_init_nonexistent_private_key_raises_filenotfound(self, monkeypatch):
        """When private key file path does not exist on disk, raises FileNotFoundError."""
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.iam.gserviceaccount.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", "C:/nonexistent/path/to/key.json")
        monkeypatch.setenv("GEE_PROJECT_ID", "canopyai-test-project")

        with pytest.raises(FileNotFoundError, match="Earth Engine private key file not found"):
            initialize_earth_engine()

    def test_init_success_with_file_path(self, monkeypatch, tmp_path):
        """When valid credentials and key file exist, initializes successfully."""
        key_file = tmp_path / "dummy_key.json"
        key_file.write_text('{"type": "service_account"}')

        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.iam.gserviceaccount.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("GEE_PROJECT_ID", "canopyai-project")

        with patch("ee.ServiceAccountCredentials") as mock_creds, \
             patch("ee.Initialize") as mock_init:
            initialize_earth_engine()

            mock_creds.assert_called_once_with(
                "sa@example.iam.gserviceaccount.com",
                key_file=str(key_file),
            )
            mock_init.assert_called_once_with(mock_creds.return_value, project="canopyai-project")

    def test_init_success_with_json_key_string(self, monkeypatch):
        """When key is provided as raw JSON string, passes key_data to ServiceAccountCredentials."""
        json_key = '{"type": "service_account", "project_id": "test"}'
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.iam.gserviceaccount.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", json_key)
        monkeypatch.setenv("GEE_PROJECT_ID", "canopyai-project")

        with patch("ee.ServiceAccountCredentials") as mock_creds, \
             patch("ee.Initialize") as mock_init:
            initialize_earth_engine()

            mock_creds.assert_called_once_with(
                "sa@example.iam.gserviceaccount.com",
                key_data=json_key,
            )
            mock_init.assert_called_once_with(mock_creds.return_value, project="canopyai-project")

    def test_init_idempotency_executes_once(self, monkeypatch, tmp_path):
        """Subsequent calls to initialize_earth_engine do not re-run unless force=True."""
        key_file = tmp_path / "key.json"
        key_file.write_text("{}")
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("GEE_PROJECT_ID", "test-proj")

        with patch("ee.ServiceAccountCredentials"), patch("ee.Initialize") as mock_init:
            initialize_earth_engine()
            assert mock_init.call_count == 1

            # Second call should be a no-op
            initialize_earth_engine()
            assert mock_init.call_count == 1

            # Forcing re-initialization calls again
            initialize_earth_engine(force=True)
            assert mock_init.call_count == 2

    def test_init_failure_raises_runtime_error(self, monkeypatch, tmp_path):
        """When ee.Initialize raises an exception, wraps it in RuntimeError."""
        key_file = tmp_path / "key.json"
        key_file.write_text("{}")
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("GEE_PROJECT_ID", "test-proj")

        with patch("ee.ServiceAccountCredentials"), \
             patch("ee.Initialize", side_effect=Exception("API connection refused")), \
             pytest.raises(RuntimeError, match="Failed to initialize Earth Engine"):
            initialize_earth_engine()


# ============================================================================
# 2. Valid Polygon Input Tests
# ============================================================================


class TestPolygonInputValidation:
    """Tests covering polygon parsing and conversion to Earth Engine geometries."""

    @patch("ee.Geometry.Polygon")
    def test_convert_geojson_dict(self, mock_poly, amazon_polygon_dict):
        """Valid GeoJSON Polygon dict converts to ee.Geometry.Polygon."""
        mock_poly.return_value = "mock_ee_geom"
        geom = polygon_to_ee_geometry(amazon_polygon_dict)
        assert geom == "mock_ee_geom"
        mock_poly.assert_called_once()

    @patch("ee.Geometry.Polygon")
    def test_convert_geojson_feature(self, mock_poly, amazon_feature_dict):
        """Valid GeoJSON Feature dict converts to ee.Geometry.Polygon."""
        mock_poly.return_value = "mock_ee_geom"
        geom = polygon_to_ee_geometry(amazon_feature_dict)
        assert geom == "mock_ee_geom"
        mock_poly.assert_called_once()

    @patch("ee.Geometry.Polygon")
    def test_convert_shapely_polygon(self, mock_poly, amazon_shapely_poly):
        """Valid Shapely Polygon converts to ee.Geometry.Polygon."""
        mock_poly.return_value = "mock_ee_geom"
        geom = polygon_to_ee_geometry(amazon_shapely_poly)
        assert geom == "mock_ee_geom"
        mock_poly.assert_called_once()

    @patch("ee.Geometry.Polygon")
    def test_convert_pydantic_schema(self, mock_poly, amazon_pydantic_poly):
        """Valid GeoJSONPolygon pydantic schema converts to ee.Geometry.Polygon."""
        mock_poly.return_value = "mock_ee_geom"
        geom = polygon_to_ee_geometry(amazon_pydantic_poly)
        assert geom == "mock_ee_geom"
        mock_poly.assert_called_once()

    @patch("ee.Geometry.Polygon")
    def test_convert_polygon_with_interior_holes(self, mock_poly):
        """Polygon with interior holes passes both exterior and interior rings."""
        mock_poly.return_value = "mock_ee_geom"
        poly_with_hole = {
            "type": "Polygon",
            "coordinates": [
                [[-60.0, -3.0], [-60.0, -2.0], [-59.0, -2.0], [-59.0, -3.0], [-60.0, -3.0]],
                [[-59.8, -2.8], [-59.8, -2.2], [-59.2, -2.2], [-59.2, -2.8], [-59.8, -2.8]],
            ],
        }
        polygon_to_ee_geometry(poly_with_hole)
        call_coords = mock_poly.call_args[0][0]
        assert len(call_coords) == 2  # Exterior ring + 1 hole

    def test_convert_none_raises_type_error(self):
        """None polygon raises TypeError."""
        with pytest.raises(TypeError, match="cannot be None"):
            polygon_to_ee_geometry(None)

    def test_convert_unclosed_polygon_raises_value_error(self):
        """Unclosed polygon ring raises ValueError."""
        unclosed = {
            "type": "Polygon",
            "coordinates": [[[-60.0, -3.0], [-60.0, -2.9], [-59.9, -2.9], [-59.9, -3.0]]],
        }
        with pytest.raises(ValueError, match="Invalid polygon geometry"):
            polygon_to_ee_geometry(unclosed)

    def test_convert_out_of_bounds_coords_raises_value_error(self):
        """Coordinates outside valid WGS84 bounds raise ValueError."""
        out_of_bounds = {
            "type": "Polygon",
            "coordinates": [[[200.0, -3.0], [200.0, -2.9], [200.1, -2.9], [200.1, -3.0], [200.0, -3.0]]],
        }
        with pytest.raises(ValueError, match="Invalid polygon geometry"):
            polygon_to_ee_geometry(out_of_bounds)


# ============================================================================
# 3. NASA GEDI Biomass Extraction Tests
# ============================================================================


class TestGediBiomassExtraction:
    """Tests covering NASA GEDI Level 4A above-ground biomass retrieval."""

    def test_gedi_biomass_success(self, amazon_polygon_dict):
        """Successful GEDI L4A query returns correct biomass statistics."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter"):

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {
                "count": 48,
                "mean": 175.4321,
                "total_sd": 31.8765,
            }

            result = get_gedi_biomass(amazon_polygon_dict)

            assert result["gedi_data_available"] is True
            assert result["gedi_observation_count"] == 48
            assert result["agb_t_per_ha"] == 175.4321
            assert result["agb_stddev"] == 31.8765
            mock_fc.assert_called_with(GEDI_L4A_COLLECTION)

    def test_gedi_biomass_filters_verified(self, amazon_polygon_dict):
        """Verifies filtering by bounds, notNull, l4_quality_flag, degrade_flag, and agbd >= 0."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter") as mock_filter:

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {"count": 10, "mean": 120.0, "total_sd": 15.0}

            get_gedi_biomass(amazon_polygon_dict)

            mock_coll.filterBounds.assert_called_once_with("mock_geom")
            mock_filter.eq.assert_any_call("l4_quality_flag", 1)
            mock_filter.eq.assert_any_call("degrade_flag", 0)
            mock_filter.gte.assert_any_call("agbd", 0.0)
            mock_filter.notNull.assert_called_with(["agbd"])


# ============================================================================
# 4. Missing GEDI Observations Tests
# ============================================================================


class TestMissingGediObservations:
    """Tests ensuring missing GEDI observations return nulls rather than invented figures."""

    def test_gedi_biomass_zero_footprints_returns_none(self, amazon_polygon_dict):
        """When 0 footprints are found, returns null values and gedi_data_available=False."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter"):

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {
                "count": 0,
                "mean": None,
                "total_sd": None,
            }

            result = get_gedi_biomass(amazon_polygon_dict)

            assert result["gedi_data_available"] is False
            assert result["gedi_observation_count"] == 0
            assert result["agb_t_per_ha"] is None
            assert result["agb_stddev"] is None

    def test_gedi_biomass_nan_mean_returns_none(self, amazon_polygon_dict):
        """When Earth Engine returns NaN for mean, treats observation as missing."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter"):

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {
                "count": 5,
                "mean": float("nan"),
                "total_sd": float("nan"),
            }

            result = get_gedi_biomass(amazon_polygon_dict)

            assert result["gedi_data_available"] is False
            assert result["agb_t_per_ha"] is None


# ============================================================================
# 5. NASA GEDI Canopy Height Extraction Tests
# ============================================================================


class TestGediCanopyHeightExtraction:
    """Tests covering NASA GEDI Level 2A monthly canopy height (RH98) extraction."""

    def test_gedi_canopy_height_success(self, amazon_polygon_dict):
        """Successful GEDI L2A query returns mean canopy height and count."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 6
            mock_masked = MagicMock()
            mock_coll.map.return_value.select.return_value = mock_masked
            mock_mean = MagicMock()
            mock_masked.mean.return_value = mock_mean
            mock_mean.reduceRegion.return_value.getInfo.return_value = {
                "rh98_mean": 27.6543,
                "rh98_count": 142,
            }

            result = get_gedi_canopy_height(amazon_polygon_dict)

            assert result["height_data_available"] is True
            assert result["mean_canopy_height_m"] == 27.6543
            assert result["height_observation_count"] == 142
            mock_ic.assert_called_with(GEDI_L2A_COLLECTION)

    def test_gedi_canopy_height_empty_collection_returns_none(self, amazon_polygon_dict):
        """When no GEDI L2A monthly rasters cover the area, returns None values."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic:

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 0

            result = get_gedi_canopy_height(amazon_polygon_dict)

            assert result["height_data_available"] is False
            assert result["mean_canopy_height_m"] is None
            assert result["height_observation_count"] == 0


# ============================================================================
# 6. ESA Sentinel-2 NDVI Calculation Tests
# ============================================================================


class TestSentinelNdviCalculation:
    """Tests covering Sentinel-2 SR harmonized imagery, cloud masking, and NDVI computation."""

    def test_sentinel_ndvi_success(self, amazon_polygon_dict):
        """Calculates mean NDVI and valid pixel percentage with cloud masking."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("app.core.earth_engine.calculate_area_ha", return_value=100.0), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 15
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            # 100 ha * 100 pixels/ha = 10,000 expected pixels. 8,800 valid -> 88.0%
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {
                "ndvi_mean": 0.8145,
                "ndvi_count": 8800,
            }

            result = get_sentinel_ndvi(
                amazon_polygon_dict,
                start_date="2024-01-01",
                end_date="2024-12-31",
            )

            assert result["mean_ndvi"] == 0.8145
            assert result["valid_pixel_percentage"] == 88.0
            assert result["image_count"] == 15
            assert result["analysis_start_date"] == "2024-01-01"
            assert result["analysis_end_date"] == "2024-12-31"
            mock_ic.assert_called_with(SENTINEL_2_COLLECTION)
            mock_comp.normalizedDifference.assert_called_with(["B8", "B4"])


# ============================================================================
# 7. Missing Cloud-Free Imagery Tests
# ============================================================================


class TestMissingCloudFreeImagery:
    """Tests handling situations where cloud cover completely obscures the forest."""

    def test_all_cloudy_returns_none_ndvi(self, amazon_polygon_dict):
        """When 100% of pixels are cloud-contaminated, returns mean_ndvi=None and 0% valid."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("app.core.earth_engine.calculate_area_ha", return_value=100.0), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 8
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            # All pixels masked out by SCL / QA60
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {
                "ndvi_mean": None,
                "ndvi_count": 0,
            }

            result = get_sentinel_ndvi(amazon_polygon_dict)

            assert result["mean_ndvi"] is None
            assert result["valid_pixel_percentage"] == 0.0
            assert result["image_count"] == 8


# ============================================================================
# 8. Quarterly NDVI Trend Generation Tests
# ============================================================================


class TestQuarterlyNdviTrend:
    """Tests covering 5-year quarterly NDVI trend generation (20 quarters target)."""

    def test_get_recent_complete_years_dynamic(self):
        """Dynamically computes 5 recent complete years, never hardcoding."""
        ref = datetime(2026, 6, 15, tzinfo=timezone.utc)
        years = get_recent_complete_years(count=5, reference_date=ref)
        assert years == [2021, 2022, 2023, 2024, 2025]
        assert len(years) == 5

    def test_ndvi_trend_produces_twenty_observations(self, amazon_polygon_dict):
        """Generates exactly 20 quarterly observations for 5 complete calendar years."""
        test_years = [2021, 2022, 2023, 2024, 2025]

        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 4
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {"ndvi": 0.775}

            trend = get_ndvi_trend(amazon_polygon_dict, years=test_years)

            assert len(trend) == 20
            # Verify chronological sequencing and quarter keys
            assert trend[0]["quarter"] == "2021-Q1"
            assert trend[0]["ndvi"] == 0.775
            assert trend[19]["quarter"] == "2025-Q4"
            assert trend[19]["ndvi"] == 0.775

    def test_ndvi_trend_missing_data_quarters_return_none(self, amazon_polygon_dict):
        """Quarters without clear satellite data return None rather than synthetic values."""
        test_years = [2025]

        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            # Simulate Q1 has 0 images, others have valid images
            mock_coll.size.return_value.getInfo.side_effect = [0, 3, 2, 4]
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {"ndvi": 0.81}

            trend = get_ndvi_trend(amazon_polygon_dict, years=test_years)

            assert len(trend) == 4
            assert trend[0]["quarter"] == "2025-Q1"
            assert trend[0]["ndvi"] is None  # Empty collection returns None
            assert trend[1]["quarter"] == "2025-Q2"
            assert trend[1]["ndvi"] == 0.81


# ============================================================================
# 9. Empty Satellite Datasets Tests
# ============================================================================


class TestEmptyDatasets:
    """Tests handling completely empty satellite datasets."""

    def test_empty_sentinel2_dataset(self, amazon_polygon_dict):
        """When Sentinel-2 has 0 images in the area, gracefully returns empty metrics."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic:

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 0

            res = get_sentinel_ndvi(amazon_polygon_dict)

            assert res["image_count"] == 0
            assert res["mean_ndvi"] is None
            assert res["valid_pixel_percentage"] == 0.0

    def test_empty_gedi_biomass_dataset(self, amazon_polygon_dict):
        """When GEDI L4A aggregate_stats returns None/empty, handles cleanly."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.FeatureCollection") as mock_fc, \
             patch("ee.Filter"):

            mock_coll = MagicMock()
            mock_fc.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filter.return_value = mock_coll
            mock_coll.aggregate_stats.return_value.getInfo.return_value = {}

            res = get_gedi_biomass(amazon_polygon_dict)

            assert res["gedi_data_available"] is False
            assert res["agb_t_per_ha"] is None


# ============================================================================
# 10. Earth Engine Service Failures & Error Handling Tests
# ============================================================================


class TestEarthEngineServiceFailures:
    """Tests graceful degradation and resilience against network timeouts or API errors."""

    def test_gedi_biomass_failure_returns_indicators_by_default(self, amazon_polygon_dict):
        """When Earth Engine query times out or raises an exception, returns safe null indicators."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=Exception("EE API timeout")):

            res = get_gedi_biomass(amazon_polygon_dict)

            assert res["gedi_data_available"] is False
            assert res["agb_t_per_ha"] is None
            assert res["gedi_observation_count"] == 0

    def test_gedi_biomass_failure_raises_when_requested(self, amazon_polygon_dict):
        """When raise_on_error=True, re-raises the underlying Earth Engine error."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=RuntimeError("Connection lost")), \
             pytest.raises(RuntimeError, match="Connection lost"):
            get_gedi_biomass(amazon_polygon_dict, raise_on_error=True)

    def test_sentinel_ndvi_failure_returns_safe_indicators(self, amazon_polygon_dict):
        """When Sentinel-2 processing fails, returns safe availability indicators."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=Exception("Quota exceeded")):

            res = get_sentinel_ndvi(amazon_polygon_dict)

            assert res["mean_ndvi"] is None
            assert res["valid_pixel_percentage"] == 0.0
            assert res["image_count"] == 0

    def test_ndvi_trend_failure_returns_twenty_null_quarters(self, amazon_polygon_dict):
        """When entire trend query fails, returns 20 null quarters rather than crashing."""
        test_years = [2021, 2022, 2023, 2024, 2025]
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", side_effect=Exception("GEE unavailable")):

            trend = get_ndvi_trend(amazon_polygon_dict, years=test_years)

            assert len(trend) == 20
            assert all(item["ndvi"] is None for item in trend)

    def test_get_satellite_observations_structured_output_contract(self, amazon_polygon_dict):
        """Combined observations function returns complete structured dictionary."""
        with patch("app.core.earth_engine.get_gedi_biomass") as mock_bio, \
             patch("app.core.earth_engine.get_gedi_canopy_height") as mock_height, \
             patch("app.core.earth_engine.get_sentinel_ndvi") as mock_s2, \
             patch("app.core.earth_engine.get_ndvi_trend") as mock_trend:

            mock_bio.return_value = {
                "agb_t_per_ha": 210.5,
                "agb_stddev": 32.1,
                "gedi_observation_count": 35,
                "gedi_data_available": True,
            }
            mock_height.return_value = {
                "mean_canopy_height_m": 29.4,
                "height_observation_count": 78,
                "height_data_available": True,
            }
            mock_s2.return_value = {
                "mean_ndvi": 0.835,
                "valid_pixel_percentage": 94.5,
                "image_count": 18,
                "analysis_start_date": "2024-01-01",
                "analysis_end_date": "2024-12-31",
            }
            mock_trend.return_value = [{"quarter": "2025-Q1", "ndvi": 0.82}]

            obs = get_satellite_observations(amazon_polygon_dict)

            # Strict field presence check required by Section 10
            required_fields = [
                "agb_t_per_ha",
                "agb_stddev",
                "gedi_observation_count",
                "gedi_data_available",
                "mean_canopy_height_m",
                "height_observation_count",
                "height_data_available",
                "mean_ndvi",
                "valid_pixel_percentage",
                "image_count",
                "ndvi_trend",
                "data_sources",
            ]
            for field in required_fields:
                assert field in obs, f"Missing required output field: {field}"

            assert obs["agb_t_per_ha"] == 210.5
            assert obs["mean_canopy_height_m"] == 29.4
            assert obs["mean_ndvi"] == 0.835
            assert obs["data_sources"] == DATA_SOURCES
            assert GEDI_L4A_COLLECTION in obs["data_sources"]
            assert GEDI_L2A_COLLECTION in obs["data_sources"]
            assert SENTINEL_2_COLLECTION in obs["data_sources"]


# ============================================================================
# 11. Forest Classification Tests
# ============================================================================


class TestForestClassifier:
    """Tests covering forest biome classification."""

    def test_classify_tropical_forest(self, amazon_polygon_dict):
        """Amazon coordinates (-3° S) classified as Tropical Moist Broadleaf."""
        assert classify_forest_type(amazon_polygon_dict) == "Tropical Moist Broadleaf"

    def test_classify_temperate_forest(self):
        """Central Europe coordinates (48° N) classified as Temperate Broadleaf."""
        temperate_poly = {
            "type": "Polygon",
            "coordinates": [
                [[8.0, 48.0], [8.0, 48.1], [8.1, 48.1], [8.1, 48.0], [8.0, 48.0]]
            ],
        }
        assert classify_forest_type(temperate_poly) == "Temperate Broadleaf"

    def test_classify_boreal_forest(self):
        """Scandinavia / Siberia coordinates (62° N) classified as Boreal Coniferous."""
        boreal_poly = {
            "type": "Polygon",
            "coordinates": [
                [[25.0, 62.0], [25.0, 62.1], [25.1, 62.1], [25.1, 62.0], [25.0, 62.0]]
            ],
        }
        assert classify_forest_type(boreal_poly) == "Boreal Coniferous"

    def test_classify_polar_tundra_other(self):
        """High Arctic coordinates (78° N) classified as Other."""
        polar_poly = {
            "type": "Polygon",
            "coordinates": [
                [[15.0, 78.0], [15.0, 78.1], [15.1, 78.1], [15.1, 78.0], [15.0, 78.0]]
            ],
        }
        assert classify_forest_type(polar_poly) == "Other"

    def test_classify_none_raises_type_error(self):
        """Passing None raises TypeError."""
        with pytest.raises(TypeError, match="cannot be None"):
            classify_forest_type(None)

    def test_classify_with_worldcover_water_returns_other(self, amazon_polygon_dict):
        """When Earth Engine is initialized and WorldCover indicates water (code 80), returns Other."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("ee.Geometry.Point"), \
             patch("ee.Image") as mock_img, \
             patch("ee.Reducer"):
            mock_img.return_value.reduceRegion.return_value.getInfo.return_value = {"Map": 80}
            result = classify_forest_type(amazon_polygon_dict)
            assert result == "Other"

    def test_classify_with_worldcover_tree_cover_returns_biome(self, amazon_polygon_dict):
        """When Earth Engine indicates tree cover (code 10), returns standard geographic biome."""
        with patch("ee.data.is_initialized", return_value=True), \
             patch("ee.Geometry.Point"), \
             patch("ee.Image") as mock_img, \
             patch("ee.Reducer"):
            mock_img.return_value.reduceRegion.return_value.getInfo.return_value = {"Map": 10}
            result = classify_forest_type(amazon_polygon_dict)
            assert result == "Tropical Moist Broadleaf"


# ============================================================================
# 12. Direct Component & Quality Masking Unit Tests
# ============================================================================


class TestInternalComponentMechanics:
    """Tests covering masking helpers, default parameter logic, and edge reduction flows."""

    def test_mask_sentinel2_sr_execution(self):
        """Direct test of _mask_sentinel2_sr exercising SCL and QA60 bitmask operations."""
        from app.core.earth_engine import _mask_sentinel2_sr

        mock_img = MagicMock()
        mock_scl = MagicMock()
        mock_qa = MagicMock()
        mock_img.select.side_effect = lambda band: mock_scl if band == "SCL" else mock_qa

        _mask_sentinel2_sr(mock_img)

        mock_img.select.assert_any_call("SCL")
        mock_img.select.assert_any_call("QA60")
        mock_img.updateMask.assert_called_once()

    def test_mask_gedi_height_execution(self):
        """Direct test of _mask_gedi_height exercising quality_flag, degrade_flag, and rh98 >= 0."""
        from app.core.earth_engine import _mask_gedi_height

        mock_img = MagicMock()
        _mask_gedi_height(mock_img)

        mock_img.select.assert_any_call("quality_flag")
        mock_img.select.assert_any_call("degrade_flag")
        mock_img.select.assert_any_call("rh98")
        mock_img.updateMask.assert_called_once()

    def test_ensure_initialized_calls_init_when_uninitialized(self, monkeypatch, tmp_path):
        """When not yet initialized, _ensure_initialized triggers initialize_earth_engine."""
        from app.core.earth_engine import _ensure_initialized

        key_file = tmp_path / "k.json"
        key_file.write_text("{}")
        monkeypatch.setenv("GEE_SERVICE_ACCOUNT_EMAIL", "sa@example.com")
        monkeypatch.setenv("GEE_PRIVATE_KEY_PATH", str(key_file))
        monkeypatch.setenv("GEE_PROJECT_ID", "test-project")

        with patch("ee.ServiceAccountCredentials"), patch("ee.Initialize") as mock_init:
            _ensure_initialized()
            mock_init.assert_called_once()

    def test_sentinel_ndvi_default_dates(self, amazon_polygon_dict):
        """When start_date and end_date are omitted, defaults are applied and query succeeds."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("app.core.earth_engine.calculate_area_ha", return_value=50.0), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 5
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {"ndvi_mean": 0.75, "ndvi_count": 4000}

            res = get_sentinel_ndvi(amazon_polygon_dict)

            assert res["mean_ndvi"] == 0.75
            assert res["analysis_start_date"] is not None
            assert res["analysis_end_date"] is not None

    def test_sentinel_ndvi_raise_on_error(self, amazon_polygon_dict):
        """When raise_on_error=True, Sentinel-2 error is re-raised."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection", side_effect=RuntimeError("S2 service error")), \
             pytest.raises(RuntimeError, match="S2 service error"):
            get_sentinel_ndvi(amazon_polygon_dict, raise_on_error=True)

    def test_gedi_canopy_height_raise_on_error(self, amazon_polygon_dict):
        """When raise_on_error=True, canopy height error is re-raised."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection", side_effect=RuntimeError("Height error")), \
             pytest.raises(RuntimeError, match="Height error"):
            get_gedi_canopy_height(amazon_polygon_dict, raise_on_error=True)

    def test_gedi_canopy_height_empty_stats_returns_none(self, amazon_polygon_dict):
        """When reduceRegion returns None, returns height_data_available=False."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 2
            mock_masked = MagicMock()
            mock_coll.map.return_value.select.return_value = mock_masked
            mock_mean = MagicMock()
            mock_masked.mean.return_value = mock_mean
            mock_mean.reduceRegion.return_value.getInfo.return_value = None

            res = get_gedi_canopy_height(amazon_polygon_dict)
            assert res["height_data_available"] is False
            assert res["mean_canopy_height_m"] is None

    def test_ndvi_trend_raise_on_error(self, amazon_polygon_dict):
        """When raise_on_error=True, NDVI trend error is re-raised."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection", side_effect=RuntimeError("Trend service down")), \
             pytest.raises(RuntimeError, match="Trend service down"):
            get_ndvi_trend(amazon_polygon_dict, years=[2025], raise_on_error=True)

    def test_ndvi_trend_default_years(self, amazon_polygon_dict):
        """When years is None, dynamically computes 5 years (20 quarters)."""
        with patch("app.core.earth_engine._ensure_initialized"), \
             patch("app.core.earth_engine.polygon_to_ee_geometry", return_value="mock_geom"), \
             patch("ee.ImageCollection") as mock_ic, \
             patch("ee.Reducer"):

            mock_coll = MagicMock()
            mock_ic.return_value = mock_coll
            mock_coll.filterBounds.return_value = mock_coll
            mock_coll.filterDate.return_value = mock_coll
            mock_coll.size.return_value.getInfo.return_value = 2
            mock_masked = MagicMock()
            mock_coll.map.return_value = mock_masked
            mock_comp = MagicMock()
            mock_masked.median.return_value = mock_comp
            mock_ndvi = MagicMock()
            mock_comp.normalizedDifference.return_value.rename.return_value = mock_ndvi
            mock_ndvi.reduceRegion.return_value.getInfo.return_value = {"ndvi": 0.79}

            trend = get_ndvi_trend(amazon_polygon_dict)
            assert len(trend) == 20
