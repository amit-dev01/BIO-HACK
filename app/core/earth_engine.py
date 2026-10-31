"""Google Earth Engine (GEE) satellite data processing module for CanopyAI.

Phase 2 & Phase 3 Satellite Remote Sensing Pipeline:
- Authentication & initialization via Google Service Account.
- NASA GEDI Level 4A (LARSE/GEDI/GEDI04_A_002) for Aboveground Biomass Density (AGBD in Mg/ha = t/ha).
- NASA GEDI Level 2A (LARSE/GEDI/GEDI02_A_002_MONTHLY) for Canopy Top Height (RH98 in meters).
- ESA Sentinel-2 Harmonized (COPERNICUS/S2_SR_HARMONIZED) for surface reflectance,
  pixel-level cloud and shadow masking (SCL + QA60), NDVI, and 5-year quarterly health trends.
- Google Dynamic World (GOOGLE/DYNAMICWORLD/V1) for 10m pixel-level tree canopy cover detection.
- Multi-factor forest type and terrestrial ecoregion classification (via ESA WorldCover v200).

Scientific Integrity Guardrails:
- GEDI observations are sampled footprints, not total tree counts.
- Never invent or fabricate biomass or tree height when satellite data is missing.
- When satellite observations are missing or obscured by persistent clouds, explicit null (None)
  values and clear availability indicators are returned.
"""

from __future__ import annotations

import logging
import math
import os
from datetime import datetime, timezone
from typing import Any

import ee

from app.utils.geo import calculate_area_ha, parse_polygon

logger = logging.getLogger("canopyai.earth_engine")

# Satellite Dataset Identifiers in Google Earth Engine Catalog
GEDI_L4A_COLLECTION: str = "LARSE/GEDI/GEDI04_A_002"
GEDI_L2A_COLLECTION: str = "LARSE/GEDI/GEDI02_A_002_MONTHLY"
SENTINEL_2_COLLECTION: str = "COPERNICUS/S2_SR_HARMONIZED"
DYNAMIC_WORLD_COLLECTION: str = "GOOGLE/DYNAMICWORLD/V1"
WORLDCOVER_COLLECTION: str = "ESA/WorldCover/v200"

DATA_SOURCES: list[str] = [
    GEDI_L4A_COLLECTION,
    GEDI_L2A_COLLECTION,
    SENTINEL_2_COLLECTION,
    DYNAMIC_WORLD_COLLECTION,
    WORLDCOVER_COLLECTION,
]

# Module-level state tracking initialization status
_EE_INITIALIZED: bool = False


# ============================================================================
# 1. Earth Engine Initialization
# ============================================================================


def initialize_earth_engine(
    project_id: str | None = None,
    service_account_email: str | None = None,
    private_key_path: str | None = None,
    force: bool = False,
) -> None:
    """Initialize Google Earth Engine API authentication and session.

    Credentials must come from environment variables:
      - GEE_SERVICE_ACCOUNT_EMAIL (or EARTH_ENGINE_SERVICE_ACCOUNT)
      - GEE_PRIVATE_KEY_PATH (or EARTH_ENGINE_PRIVATE_KEY)
      - GEE_PROJECT_ID

    Initialization is idempotent and executes only once unless forced.
    If credentials are missing or invalid, raises a clear error without
    crashing mock-mode functionality.

    Args:
        project_id: Optional GCP project ID override.
        service_account_email: Optional service account email override.
        private_key_path: Optional path to service account private key file override.
        force: If True, forces re-initialization even if already initialized.

    Raises:
        RuntimeError: If required credentials are not found or initialization fails.
        FileNotFoundError: If the specified private key path does not exist.
    """
    global _EE_INITIALIZED

    # Check if already initialized
    if _EE_INITIALIZED and not force:
        return

    # Resolve configuration from arguments or environment variables
    email = (
        service_account_email
        or os.environ.get("GEE_SERVICE_ACCOUNT_EMAIL")
        or os.environ.get("EARTH_ENGINE_SERVICE_ACCOUNT")
    )
    key_path = (
        private_key_path
        or os.environ.get("GEE_PRIVATE_KEY_PATH")
        or os.environ.get("EARTH_ENGINE_PRIVATE_KEY")
    )
    project = (
        project_id
        or os.environ.get("GEE_PROJECT_ID")
    )

    missing = []
    if not email:
        missing.append("GEE_SERVICE_ACCOUNT_EMAIL")
    if not key_path:
        missing.append("GEE_PRIVATE_KEY_PATH")
    if not project:
        missing.append("GEE_PROJECT_ID")

    if missing:
        raise RuntimeError(
            f"Google Earth Engine credentials missing. Required configuration: {', '.join(missing)}. "
            "Please configure these environment variables or run in mock mode."
        )

    # Validate key path / key data
    is_raw_json = isinstance(key_path, str) and key_path.strip().startswith("{")
    if not is_raw_json and not os.path.exists(key_path):
        raise FileNotFoundError(f"Earth Engine private key file not found at: {key_path}")

    try:
        if is_raw_json:
            credentials = ee.ServiceAccountCredentials(email, key_data=key_path)
        else:
            credentials = ee.ServiceAccountCredentials(email, key_file=key_path)

        ee.Initialize(credentials, project=project)
        _EE_INITIALIZED = True
        logger.info("Google Earth Engine initialized successfully for project: %s", project)
    except Exception as exc:
        _EE_INITIALIZED = False
        logger.error("Failed to initialize Google Earth Engine: %s", exc)
        raise RuntimeError(f"Failed to initialize Earth Engine: {exc}") from exc


def reset_earth_engine() -> None:
    """Reset Earth Engine initialization state. Primarily used in test suites."""
    global _EE_INITIALIZED
    _EE_INITIALIZED = False
    try:
        if hasattr(ee, "Reset"):
            ee.Reset()
    except Exception as exc:  # noqa: BLE001
        logger.debug("ee.Reset failed during state reset: %s", exc)


def _ensure_initialized() -> None:
    """Ensure Earth Engine has been initialized prior to query execution."""
    global _EE_INITIALIZED
    if _EE_INITIALIZED:
        return
    try:
        if hasattr(ee, "data") and hasattr(ee.data, "is_initialized") and ee.data.is_initialized():
            _EE_INITIALIZED = True
            return
    except Exception as exc:  # noqa: BLE001
        logger.debug("ee.data.is_initialized check failed: %s", exc)
    initialize_earth_engine()


# ============================================================================
# 2. Geospatial Geometry Conversion Helper
# ============================================================================


def polygon_to_ee_geometry(polygon: Any) -> ee.Geometry:
    """Convert any supported polygon representation to an Earth Engine Geometry.

    Supports:
      - GeoJSON Polygon dict
      - GeoJSON Feature dict
      - Shapely Polygon object
      - Pydantic GeoJSONPolygon model
      - Raw coordinate rings

    Args:
        polygon: Polygon input geometry.

    Returns:
        ee.Geometry.Polygon in EPSG:4326 (WGS84).

    Raises:
        TypeError: If polygon is None.
        ValueError: If polygon fails geometric or coordinate validation.
    """
    if polygon is None:
        raise TypeError("Polygon input cannot be None.")

    # Support Pydantic models (e.g. GeoJSONPolygon)
    if hasattr(polygon, "model_dump"):
        polygon = polygon.model_dump()

    try:
        shapely_poly = parse_polygon(polygon)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid polygon geometry provided: {exc}") from exc

    # Extract exterior and interior rings in WGS84 coordinates
    coords: list[list[list[float]]] = [
        [list(pt) for pt in shapely_poly.exterior.coords]
    ]
    for interior in shapely_poly.interiors:
        coords.append([list(pt) for pt in interior.coords])

    return ee.Geometry.Polygon(coords, proj="EPSG:4326", geodesic=True)


# ============================================================================
# 3. NASA GEDI Level 4A Biomass Integration
# ============================================================================


def get_gedi_biomass(polygon: Any, raise_on_error: bool = False) -> dict[str, Any]:
    """Retrieve NASA GEDI Level 4A above-ground biomass density (AGBD) observations.

    Dataset:
        NASA GEDI Level 4A (LARSE/GEDI/GEDI04_A_002)
        Band / Property: agbd
        Units: Megagrams per hectare (Mg/ha = tonnes/hectare)

    Quality Filtering:
      - Spatial intersection with polygon boundary
      - l4_quality_flag == 1 (algorithmic fidelity criteria passed)
      - degrade_flag == 0 (no attitude/position degradation)
      - agbd >= 0 (positive valid biomass density, excludes fill values)

    Returns:
        Dictionary containing:
          - agb_t_per_ha: Mean AGBD in tonnes/ha (float) or None if unavailable
          - agb_stddev: Biomass standard deviation in tonnes/ha (float) or None
          - gedi_observation_count: Valid footprint count (int)
          - gedi_data_available: Boolean indicating presence of valid footprints
    """
    try:
        _ensure_initialized()
    except Exception as init_exc:
        logger.warning("Earth Engine initialization check failed in get_gedi_biomass: %s", init_exc)
        if raise_on_error:
            raise
        return {
            "agb_t_per_ha": None,
            "agb_stddev": None,
            "gedi_observation_count": 0,
            "gedi_data_available": False,
        }

    try:
        try:
            ee_geom = polygon_to_ee_geometry(polygon)
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            logger.warning("Failed converting polygon to Earth Engine geometry: %s", exc)
            if raise_on_error:
                raise
            return {
                "agb_t_per_ha": None,
                "agb_stddev": None,
                "gedi_observation_count": 0,
                "gedi_data_available": False,
            }

        collection = ee.FeatureCollection(GEDI_L4A_COLLECTION)
        filtered = (
            collection
            .filterBounds(ee_geom)
            .filter(ee.Filter.notNull(["agbd"]))
            .filter(ee.Filter.gte("agbd", 0.0))
            .filter(ee.Filter.eq("l4_quality_flag", 1))
            .filter(ee.Filter.eq("degrade_flag", 0))
        )

        stats = filtered.aggregate_stats("agbd").getInfo()

        count = int(stats.get("count", 0)) if stats else 0
        if count <= 0 or stats.get("mean") is None:
            return {
                "agb_t_per_ha": None,
                "agb_stddev": None,
                "gedi_observation_count": 0,
                "gedi_data_available": False,
            }

        mean_val = stats.get("mean")
        if mean_val is None or (isinstance(mean_val, float) and math.isnan(mean_val)):
            return {
                "agb_t_per_ha": None,
                "agb_stddev": None,
                "gedi_observation_count": count,
                "gedi_data_available": False,
            }

        sd_val = stats.get("total_sd", stats.get("sample_sd", stats.get("std_dev", 0.0)))
        sd_float = (
            round(float(sd_val), 4)
            if sd_val is not None and not (isinstance(sd_val, float) and math.isnan(sd_val))
            else None
        )

        return {
            "agb_t_per_ha": round(float(mean_val), 4),
            "agb_stddev": sd_float,
            "gedi_observation_count": count,
            "gedi_data_available": True,
        }

    except Exception as exc:
        logger.warning("Failed to retrieve NASA GEDI L4A biomass observations: %s", exc)
        if raise_on_error:
            raise
        return {
            "agb_t_per_ha": None,
            "agb_stddev": None,
            "gedi_observation_count": 0,
            "gedi_data_available": False,
        }


# ============================================================================
# 4. NASA GEDI Level 2A Canopy Height Integration
# ============================================================================


def _mask_gedi_height(image: ee.Image) -> ee.Image:
    """Mask low-quality or invalid GEDI Level 2A canopy height pixels."""
    quality = image.select("quality_flag")
    mask = quality.eq(1)

    degrade = image.select("degrade_flag")
    mask = mask.And(degrade.eq(0))

    rh98 = image.select("rh98")
    mask = mask.And(rh98.gte(0.0))

    return image.updateMask(mask)


def get_gedi_canopy_height(polygon: Any, raise_on_error: bool = False) -> dict[str, Any]:
    """Retrieve NASA GEDI Level 2A canopy top height (RH98) observations.

    Dataset:
        NASA GEDI Level 2A Monthly (LARSE/GEDI/GEDI02_A_002_MONTHLY)
        Band: rh98 (Relative Height at 98th percentile in meters)

    Quality Filtering:
      - Spatial intersection with polygon boundary
      - quality_flag == 1 (algorithmic criteria met)
      - degrade_flag == 0 (instrument in nominal operation)
      - rh98 >= 0 (non-negative canopy height)

    Returns:
        Dictionary containing:
          - mean_canopy_height_m: Mean canopy height in meters (float) or None
          - height_observation_count: Valid observed pixels count (int)
          - height_data_available: Boolean indicating presence of valid height data
    """
    try:
        _ensure_initialized()
    except Exception as init_exc:
        logger.warning("Earth Engine initialization check failed in get_gedi_canopy_height: %s", init_exc)
        if raise_on_error:
            raise
        return {
            "mean_canopy_height_m": None,
            "height_observation_count": 0,
            "height_data_available": False,
        }

    try:
        try:
            ee_geom = polygon_to_ee_geometry(polygon)
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            logger.warning("Failed converting polygon to Earth Engine geometry: %s", exc)
            if raise_on_error:
                raise
            return {
                "mean_canopy_height_m": None,
                "height_observation_count": 0,
                "height_data_available": False,
            }

        collection = ee.ImageCollection(GEDI_L2A_COLLECTION).filterBounds(ee_geom)

        col_size = int(collection.size().getInfo())
        if col_size <= 0:
            return {
                "mean_canopy_height_m": None,
                "height_observation_count": 0,
                "height_data_available": False,
            }

        masked = collection.map(_mask_gedi_height).select("rh98")
        mean_img = masked.mean()

        reducer = ee.Reducer.mean().combine(
            reducer2=ee.Reducer.count(),
            outputPrefix="",
            sharedInputs=True,
        )

        stats = mean_img.reduceRegion(
            reducer=reducer,
            geometry=ee_geom,
            scale=25,
            maxPixels=100_000_000,
        ).getInfo()

        if not stats:
            return {
                "mean_canopy_height_m": None,
                "height_observation_count": 0,
                "height_data_available": False,
            }

        mean_val = stats.get("rh98_mean", stats.get("mean"))
        count_val = int(stats.get("rh98_count", stats.get("count", 0)) or 0)

        if (
            count_val <= 0
            or mean_val is None
            or (isinstance(mean_val, float) and math.isnan(mean_val))
        ):
            return {
                "mean_canopy_height_m": None,
                "height_observation_count": 0,
                "height_data_available": False,
            }

        return {
            "mean_canopy_height_m": round(float(mean_val), 4),
            "height_observation_count": count_val,
            "height_data_available": True,
        }

    except Exception as exc:
        logger.warning("Failed to retrieve NASA GEDI canopy height observations: %s", exc)
        if raise_on_error:
            raise
        return {
            "mean_canopy_height_m": None,
            "height_observation_count": 0,
            "height_data_available": False,
        }


# ============================================================================
# 5. ESA Sentinel-2 Harmonized Surface Reflectance & NDVI
# ============================================================================


def _mask_sentinel2_sr(image: ee.Image) -> ee.Image:
    """Apply pixel-level cloud and cloud-shadow masking to Sentinel-2 SR imagery.

    Utilizes Sen2Cor Scene Classification Layer (SCL) and QA60 bitmask:
      - SCL classes excluded:
          0 = No data
          1 = Saturated or defective
          3 = Cloud shadows
          8 = Cloud medium probability
          9 = Cloud high probability
          10 = Thin cirrus
          11 = Snow or ice
      - QA60 bits excluded:
          Bit 10 = Opaque clouds
          Bit 11 = Cirrus clouds

    Retains clean vegetation, bare ground, and clear water surface pixels.
    """
    scl = image.select("SCL")
    qa = image.select("QA60")

    # Unwanted SCL classes
    unwanted = scl.eq(0).Or(scl.eq(1)).Or(scl.eq(3)).Or(scl.gte(8))
    scl_mask = unwanted.Not()

    # QA60 cloud bitmasks
    cloud_bit = 1 << 10
    cirrus_bit = 1 << 11
    qa_mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))

    valid_mask = scl_mask.And(qa_mask)
    return image.updateMask(valid_mask)


def get_sentinel_ndvi(
    polygon: Any,
    start_date: str | None = None,
    end_date: str | None = None,
    raise_on_error: bool = False,
) -> dict[str, Any]:
    """Retrieve Sentinel-2 imagery, apply cloud masking, and calculate mean NDVI.

    Dataset:
        ESA Sentinel-2 Harmonized Surface Reflectance (COPERNICUS/S2_SR_HARMONIZED)
        NDVI Formula: (B8 - B4) / (B8 + B4)
          where B8 = NIR (Near-Infrared), B4 = RED

    Args:
        polygon: Evaluation boundary.
        start_date: Analysis start date (ISO string YYYY-MM-DD). Defaults to 365 days prior.
        end_date: Analysis end date (ISO string YYYY-MM-DD). Defaults to current date.
        raise_on_error: If True, re-raises query exceptions.

    Returns:
        Dictionary containing:
          - mean_ndvi: Mean NDVI across valid polygon pixels (float) or None
          - valid_pixel_percentage: Percentage of cloud-free pixels (0.0 to 100.0)
          - image_count: Number of Sentinel-2 scenes covering the area (int)
          - analysis_start_date: Start date string
          - analysis_end_date: End date string
    """
    now_utc = datetime.now(timezone.utc)
    if not end_date:
        end_date = now_utc.strftime("%Y-%m-%d")
    if not start_date:
        start_year = now_utc.year - 1
        start_date = f"{start_year}-{now_utc.strftime('%m-%d')}"

    try:
        _ensure_initialized()
    except Exception as init_exc:
        logger.warning("Earth Engine initialization check failed in get_sentinel_ndvi: %s", init_exc)
        if raise_on_error:
            raise
        return {
            "mean_ndvi": None,
            "valid_pixel_percentage": 0.0,
            "image_count": 0,
            "analysis_start_date": start_date,
            "analysis_end_date": end_date,
        }

    try:
        try:
            ee_geom = polygon_to_ee_geometry(polygon)
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            logger.warning("Failed converting polygon to Earth Engine geometry: %s", exc)
            if raise_on_error:
                raise
            return {
                "mean_ndvi": None,
                "valid_pixel_percentage": 0.0,
                "image_count": 0,
                "analysis_start_date": start_date,
                "analysis_end_date": end_date,
            }

        raw_collection = (
            ee.ImageCollection(SENTINEL_2_COLLECTION)
            .filterBounds(ee_geom)
            .filterDate(start_date, end_date)
        )

        image_count = int(raw_collection.size().getInfo())
        if image_count <= 0:
            return {
                "mean_ndvi": None,
                "valid_pixel_percentage": 0.0,
                "image_count": 0,
                "analysis_start_date": start_date,
                "analysis_end_date": end_date,
            }

        # Apply pixel-level cloud and shadow masking
        masked_collection = raw_collection.map(_mask_sentinel2_sr)

        # Generate median surface reflectance composite
        composite = masked_collection.median()
        ndvi_img = composite.normalizedDifference(["B8", "B4"]).rename("ndvi")

        reducer = ee.Reducer.mean().combine(
            reducer2=ee.Reducer.count(),
            outputPrefix="",
            sharedInputs=True,
        )

        stats = ndvi_img.reduceRegion(
            reducer=reducer,
            geometry=ee_geom,
            scale=10,
            maxPixels=100_000_000,
        ).getInfo()

        if not stats:
            return {
                "mean_ndvi": None,
                "valid_pixel_percentage": 0.0,
                "image_count": image_count,
                "analysis_start_date": start_date,
                "analysis_end_date": end_date,
            }

        mean_val = stats.get("ndvi_mean", stats.get("mean"))
        valid_pixel_count = int(stats.get("ndvi_count", stats.get("count", 0)) or 0)

        # Compute valid pixel coverage percentage relative to polygon area (1 ha = 100 pixels at 10m scale)
        area_ha = calculate_area_ha(polygon)
        expected_pixels = max(1, round(area_ha * 100.0))
        valid_pixel_pct = min(100.0, round((valid_pixel_count / expected_pixels) * 100.0, 2))

        if (
            valid_pixel_count <= 0
            or mean_val is None
            or (isinstance(mean_val, float) and math.isnan(mean_val))
        ):
            return {
                "mean_ndvi": None,
                "valid_pixel_percentage": 0.0,
                "image_count": image_count,
                "analysis_start_date": start_date,
                "analysis_end_date": end_date,
            }

        return {
            "mean_ndvi": round(float(mean_val), 4),
            "valid_pixel_percentage": valid_pixel_pct,
            "image_count": image_count,
            "analysis_start_date": start_date,
            "analysis_end_date": end_date,
        }

    except Exception as exc:
        logger.warning("Failed to calculate Sentinel-2 NDVI: %s", exc)
        if raise_on_error:
            raise
        return {
            "mean_ndvi": None,
            "valid_pixel_percentage": 0.0,
            "image_count": 0,
            "analysis_start_date": start_date,
            "analysis_end_date": end_date,
        }


# ============================================================================
# 6. Vegetation Health Trend (5 Recent Complete Years, Quarterly NDVI)
# ============================================================================


def get_recent_complete_years(count: int = 5, reference_date: datetime | None = None) -> list[int]:
    """Return the most recent `count` complete calendar years.

    Dynamically calculates years relative to the current calendar date without
    hardcoding fixed date ranges.

    Args:
        count: Number of calendar years to retrieve (default: 5).
        reference_date: Optional reference datetime (defaults to UTC now).

    Returns:
        List of integer years in chronological order (e.g. [2021, 2022, 2023, 2024, 2025]).
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    current_year = reference_date.year
    return list(range(current_year - count, current_year))


def get_ndvi_trend(
    polygon: Any,
    years: list[int] | None = None,
    raise_on_error: bool = False,
) -> list[dict[str, Any]]:
    """Calculate quarterly NDVI observations across the 5 most recent complete calendar years.

    Target:
        20 quarterly observations (4 quarters per year: Q1, Q2, Q3, Q4).
        Each observation contains:
          - quarter: String identifier (e.g., '2025-Q1')
          - ndvi: Mean NDVI (float) or None if insufficient clear data exists.

    Args:
        polygon: Evaluation boundary.
        years: Optional list of integer years. Defaults to 5 most recent complete years.
        raise_on_error: If True, re-raises query exceptions.

    Returns:
        List of 20 observation dictionaries [{'quarter': 'YYYY-QX', 'ndvi': float | None}, ...]
    """
    if years is None:
        years = get_recent_complete_years(count=5)

    quarter_definitions = [
        ("Q1", "01-01", "04-01"),
        ("Q2", "04-01", "07-01"),
        ("Q3", "07-01", "10-01"),
        ("Q4", "10-01", "01-01"),
    ]

    try:
        _ensure_initialized()
    except Exception as init_exc:
        logger.warning("Earth Engine initialization check failed in get_ndvi_trend: %s", init_exc)
        if raise_on_error:
            raise
        fallback = []
        for y in years:
            for q_name, _, _ in quarter_definitions:
                fallback.append({"quarter": f"{y}-{q_name}", "ndvi": None})
        return fallback

    results: list[dict[str, Any]] = []

    try:
        try:
            ee_geom = polygon_to_ee_geometry(polygon)
        except (TypeError, ValueError):
            raise
        except Exception as exc:
            logger.warning("Failed converting polygon to Earth Engine geometry: %s", exc)
            if raise_on_error:
                raise
            fallback = []
            for year in years:
                for q_name, _, _ in quarter_definitions:
                    fallback.append({"quarter": f"{year}-{q_name}", "ndvi": None})
            return fallback

        # Pre-filter Sentinel-2 collection to the entire 5-year bounds to optimize caching
        start_bound = f"{years[0]}-01-01"
        end_bound = f"{years[-1] + 1}-01-01"

        base_collection = (
            ee.ImageCollection(SENTINEL_2_COLLECTION)
            .filterBounds(ee_geom)
            .filterDate(start_bound, end_bound)
        )

        for year in years:
            for q_name, start_md, end_md in quarter_definitions:
                q_label = f"{year}-{q_name}"
                q_start = f"{year}-{start_md}"
                q_end = f"{year + 1}-{end_md}" if q_name == "Q4" else f"{year}-{end_md}"

                try:
                    q_col = base_collection.filterDate(q_start, q_end)
                    q_size = int(q_col.size().getInfo())

                    if q_size <= 0:
                        results.append({"quarter": q_label, "ndvi": None})
                        continue

                    # Cloud mask and median composite
                    masked = q_col.map(_mask_sentinel2_sr)
                    composite = masked.median()
                    ndvi_img = composite.normalizedDifference(["B8", "B4"]).rename("ndvi")

                    stats = ndvi_img.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=ee_geom,
                        scale=20,
                        maxPixels=50_000_000,
                    ).getInfo()

                    val = stats.get("ndvi") if stats else None
                    if val is not None and not (isinstance(val, float) and math.isnan(val)):
                        results.append({"quarter": q_label, "ndvi": round(float(val), 4)})
                    else:
                        results.append({"quarter": q_label, "ndvi": None})

                except Exception as q_exc:  # noqa: BLE001
                    logger.debug("Quarter %s NDVI calculation failed: %s", q_label, q_exc)
                    results.append({"quarter": q_label, "ndvi": None})

        return results

    except Exception as exc:
        logger.warning("Failed to calculate NDVI trend: %s", exc)
        if raise_on_error:
            raise
        # Generate full 20 null quarters on total query failure
        fallback = []
        for year in years:
            for q_name, _, _ in quarter_definitions:
                fallback.append({"quarter": f"{year}-{q_name}", "ndvi": None})
        return fallback


# ============================================================================
# 7. Google Dynamic World Canopy Cover Detection
# ============================================================================


def get_canopy_cover(
    polygon: Any,
    year: int | None = None,
    raise_on_error: bool = False,
) -> dict[str, Any]:
    """Estimate the percentage of the polygon area covered by tree canopy using Dynamic World.

    Dataset:
        Google Dynamic World (GOOGLE/DYNAMICWORLD/V1)
        Class Mapping: 1 = Trees (canopy), all other classes (0, 2-9) = non-canopy.
        Resolution: 10 meters

    Temporal Filtering:
        Uses the most recent complete calendar year by default.

    Returns:
        Dictionary containing:
          - canopy_cover_pct: Float between 0.0 and 100.0 (rounded to 1 decimal place) or None
          - canopy_data_available: Boolean indicating presence of valid satellite data
          - canopy_pixel_count: Integer count of valid pixels analyzed
    """
    if polygon is None:
        raise TypeError("Polygon input cannot be None.")

    try:
        ee_geom = polygon_to_ee_geometry(polygon)
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.warning("Failed converting polygon to Earth Engine geometry: %s", exc)
        if raise_on_error:
            raise
        return {
            "canopy_cover_pct": None,
            "canopy_data_available": False,
            "canopy_pixel_count": 0,
        }

    try:
        _ensure_initialized()
    except Exception as init_exc:
        logger.warning("Earth Engine initialization check failed in get_canopy_cover: %s", init_exc)
        if raise_on_error:
            raise
        return {
            "canopy_cover_pct": None,
            "canopy_data_available": False,
            "canopy_pixel_count": 0,
        }

    if year is None:
        year = get_recent_complete_years(1)[0]
    start_date = f"{year}-01-01"
    end_date = f"{year + 1}-01-01"

    try:
        collection = (
            ee.ImageCollection(DYNAMIC_WORLD_COLLECTION)
            .filterBounds(ee_geom)
            .filterDate(start_date, end_date)
        )

        col_size = int(collection.size().getInfo())
        if col_size <= 0:
            return {
                "canopy_cover_pct": None,
                "canopy_data_available": False,
                "canopy_pixel_count": 0,
            }

        # Select 'label' band, aggregate over time via mode, and create binary tree mask (Trees == 1)
        labels = collection.select("label")
        mode_label = labels.reduce(ee.Reducer.mode())
        tree_binary = mode_label.eq(1).rename("trees")

        reducer = ee.Reducer.mean().combine(
            reducer2=ee.Reducer.count(),
            outputPrefix="",
            sharedInputs=True,
        )

        stats = tree_binary.reduceRegion(
            reducer=reducer,
            geometry=ee_geom,
            scale=10,
            maxPixels=100_000_000,
        ).getInfo()

        if not stats:
            return {
                "canopy_cover_pct": None,
                "canopy_data_available": False,
                "canopy_pixel_count": 0,
            }

        mean_val = stats.get("trees_mean", stats.get("mean"))
        pixel_count = int(stats.get("trees_count", stats.get("count", 0)) or 0)

        if (
            pixel_count <= 0
            or mean_val is None
            or (isinstance(mean_val, float) and math.isnan(mean_val))
        ):
            return {
                "canopy_cover_pct": None,
                "canopy_data_available": False,
                "canopy_pixel_count": 0,
            }

        # Mean of 0/1 binary mask is fraction of canopy cover; multiply by 100 for percentage
        canopy_pct = max(0.0, min(100.0, round(float(mean_val) * 100.0, 1)))

        return {
            "canopy_cover_pct": canopy_pct,
            "canopy_data_available": True,
            "canopy_pixel_count": pixel_count,
        }

    except Exception as exc:
        logger.warning("Failed to calculate Dynamic World canopy cover: %s", exc)
        if raise_on_error:
            raise
        return {
            "canopy_cover_pct": None,
            "canopy_data_available": False,
            "canopy_pixel_count": 0,
        }


# ============================================================================
# 8. Combined Structured Satellite Observations
# ============================================================================


def get_satellite_observations(polygon: Any, raise_on_error: bool = False) -> dict[str, Any]:
    """Execute complete satellite remote sensing pipeline for a forest boundary.

    Aggregates:
      - NASA GEDI L4A Aboveground Biomass Density
      - NASA GEDI L2A Canopy Top Height
      - ESA Sentinel-2 Harmonized NDVI and cloud coverage
      - ESA Sentinel-2 5-Year Quarterly NDVI Vegetation Health Trends
      - Google Dynamic World Canopy Cover Percentage [Phase 3]
      - Multi-Factor Forest Type & Ecoregion Classification [Phase 3]

    Output Schema (Strict Contract for Developer 2 Integration):
      - agb_t_per_ha: float | None
      - agb_stddev: float | None
      - gedi_observation_count: int
      - gedi_data_available: bool
      - mean_canopy_height_m: float | None
      - height_observation_count: int
      - height_data_available: bool
      - mean_ndvi: float | None
      - valid_pixel_percentage: float | None
      - image_count: int
      - ndvi_trend: list[dict[str, Any]]
      - canopy_cover_pct: float | None
      - canopy_data_available: bool
      - canopy_pixel_count: int
      - forest_type: str
      - ecoregion: str
      - dominant_land_cover: str
      - classification_method: str
      - classification_confidence: str
      - recommended_standard: str | None
      - data_sources: list[str]

    Args:
        polygon: GeoJSON polygon boundary.
        raise_on_error: If True, re-raises query exceptions.

    Returns:
        Structured observation dictionary.
    """
    from app.core.forest_classifier import classify_forest_type

    # 1. GEDI Biomass
    biomass_res = get_gedi_biomass(polygon, raise_on_error=raise_on_error)

    # 2. GEDI Canopy Height
    height_res = get_gedi_canopy_height(polygon, raise_on_error=raise_on_error)

    # 3. Sentinel-2 Current Condition NDVI
    s2_res = get_sentinel_ndvi(polygon, raise_on_error=raise_on_error)

    # 4. Sentinel-2 5-Year Quarterly NDVI Trend
    trend_res = get_ndvi_trend(polygon, raise_on_error=raise_on_error)

    # 5. Google Dynamic World Canopy Cover [Phase 3]
    canopy_res = get_canopy_cover(polygon, raise_on_error=raise_on_error)

    # 6. Multi-Factor Forest Classification [Phase 3]
    classifier_res = classify_forest_type(polygon, mean_ndvi=s2_res.get("mean_ndvi"))

    return {
        "agb_t_per_ha": biomass_res["agb_t_per_ha"],
        "agb_stddev": biomass_res["agb_stddev"],
        "gedi_observation_count": biomass_res["gedi_observation_count"],
        "gedi_data_available": biomass_res["gedi_data_available"],
        "mean_canopy_height_m": height_res["mean_canopy_height_m"],
        "height_observation_count": height_res["height_observation_count"],
        "height_data_available": height_res["height_data_available"],
        "mean_ndvi": s2_res["mean_ndvi"],
        "valid_pixel_percentage": s2_res["valid_pixel_percentage"],
        "image_count": s2_res["image_count"],
        "ndvi_trend": trend_res,
        "canopy_cover_pct": canopy_res["canopy_cover_pct"],
        "canopy_data_available": canopy_res["canopy_data_available"],
        "canopy_pixel_count": canopy_res["canopy_pixel_count"],
        "forest_type": classifier_res["forest_type"],
        "ecoregion": classifier_res["ecoregion"],
        "dominant_land_cover": classifier_res["dominant_land_cover"],
        "classification_method": classifier_res["classification_method"],
        "classification_confidence": classifier_res["classification_confidence"],
        "recommended_standard": classifier_res["recommended_standard"],
        "data_sources": DATA_SOURCES,
    }
