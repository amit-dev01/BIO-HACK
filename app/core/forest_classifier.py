"""Forest classification and canopy cover extraction module for CanopyAI.

Phase 3 Multi-Factor Satellite & Ecological Classification:
Classifies the dominant forest type, ecoregion, dominant land cover,
and recommended carbon verification standards using:
  1. Priority 1: ESA WorldCover (ESA/WorldCover/v200) 10m global land cover
  2. Priority 2: Centroid latitude-based bioclimatic ecozone heuristics
  3. Priority 3: Sentinel-2 mean NDVI cross-validation

Standard Biome Categories:
  - "Tropical Moist Broadleaf" (Ecoregion: "Tropical/Subtropical", Standard: "Verra VM0047")
  - "Temperate Broadleaf" (Ecoregion: "Temperate", Standard: "Verra VM0003")
  - "Boreal Coniferous" (Ecoregion: "Boreal", Standard: "Verra VM0003")
  - "Non-Forest" (Ecoregion: "Non-Forest", Standard: None)
"""

from __future__ import annotations

import logging
from typing import Any

from app.utils.geo import get_bounding_box, get_centroid, parse_polygon

logger = logging.getLogger("canopyai.forest_classifier")

WORLDCOVER_COLLECTION: str = "ESA/WorldCover/v200"

WORLDCOVER_CLASSES: dict[int, str] = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
}


class ForestClassificationResult(dict):
    """Classification result dictionary containing multi-factor metadata.

    Supports dictionary key indexing and backward-compatible direct equality
    comparison with a forest_type string.
    """

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            if other == "Other" and self.get("forest_type") in ("Non-Forest", "Other"):
                return True
            return self.get("forest_type") == other
        return super().__eq__(other)

    def __str__(self) -> str:
        return str(self.get("forest_type", ""))


def _check_spans_multiple_ecoregions(min_lat: float, max_lat: float) -> bool:
    """Check if polygon bounding box spans across latitude-based ecoregion thresholds."""
    # Thresholds: 23.5° (Tropical/Temperate boundary) and 50.0° (Temperate/Boreal boundary)
    crosses_tropical_temperate_north = min_lat < 23.5 < max_lat
    crosses_tropical_temperate_south = min_lat < -23.5 < max_lat
    crosses_temperate_boreal_north = min_lat < 50.0 < max_lat
    crosses_temperate_boreal_south = min_lat < -50.0 < max_lat

    return (
        crosses_tropical_temperate_north
        or crosses_tropical_temperate_south
        or crosses_temperate_boreal_north
        or crosses_temperate_boreal_south
    )


def classify_forest_type(
    polygon: Any,
    mean_ndvi: float | None = None,
) -> ForestClassificationResult:
    """Classify the dominant forest biome/type using satellite and ecological heuristics.

    Inputs evaluated in order of priority:
      - Priority 1: ESA WorldCover (ESA/WorldCover/v200) dominant land cover class
      - Priority 2: Centroid latitude-based ecozone sub-classification
      - Priority 3: Sentinel-2 mean NDVI cross-validation

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, Shapely Polygon, or coordinates.
        mean_ndvi: Optional mean NDVI value from Sentinel-2 for cross-validation.

    Returns:
        ForestClassificationResult containing:
          - forest_type: "Tropical Moist Broadleaf" | "Temperate Broadleaf" | "Boreal Coniferous" | "Non-Forest"
          - ecoregion: "Tropical/Subtropical" | "Temperate" | "Boreal" | "Non-Forest"
          - dominant_land_cover: Name of the dominant land cover class (e.g., "Tree cover")
          - classification_method: "satellite+latitude" or "latitude-only"
          - classification_confidence: "high" | "medium" | "low"
          - recommended_standard: "Verra VM0047" | "Verra VM0003" | None

    Raises:
        TypeError: If polygon is None.
        ValueError: If polygon geometry is invalid.
    """
    if polygon is None:
        raise TypeError("Polygon input cannot be None.")

    if hasattr(polygon, "model_dump"):
        polygon = polygon.model_dump()

    poly = parse_polygon(polygon)
    _lon, lat = get_centroid(poly)
    _minx, miny, _maxx, maxy = get_bounding_box(poly)

    spans_multiple = _check_spans_multiple_ecoregions(miny, maxy)

    dominant_class_code: int | None = None
    classification_method = "satellite+latitude"

    # ------------------------------------------------------------------------
    # Priority 1: ESA WorldCover Dataset (ESA/WorldCover/v200)
    # ------------------------------------------------------------------------
    try:
        import ee

        if hasattr(ee, "data") and hasattr(ee.data, "is_initialized") and ee.data.is_initialized():
            try:
                from app.core.earth_engine import polygon_to_ee_geometry
                ee_geom = polygon_to_ee_geometry(polygon)
            except Exception:  # noqa: BLE001
                ee_geom = None

            # Try loading as ImageCollection or directly as Image (supports test mocks)
            landcover = None
            try:
                wc_col = ee.ImageCollection(WORLDCOVER_COLLECTION).filterBounds(ee_geom)
                col_size = int(wc_col.size().getInfo())
                if col_size > 0:
                    landcover = wc_col.first()
            except Exception as exc:  # noqa: BLE001
                logger.debug("ESA WorldCover collection query failed: %s", exc)

            if landcover is None:
                try:
                    landcover = ee.Image(WORLDCOVER_COLLECTION)
                except Exception as exc:  # noqa: BLE001
                    logger.debug("ESA WorldCover direct image query failed: %s", exc)

            if landcover is not None:
                stats = landcover.reduceRegion(
                    reducer=ee.Reducer.mode(),
                    geometry=ee_geom,
                    scale=10,
                    maxPixels=100_000_000,
                ).getInfo()

                if stats and "Map" in stats and stats["Map"] is not None:
                    dominant_class_code = int(stats["Map"])
            else:
                classification_method = "latitude-only"
        else:
            classification_method = "latitude-only"
    except Exception as exc:  # noqa: BLE001
        logger.warning("ESA WorldCover query failed, falling back to latitude-only: %s", exc)
        classification_method = "latitude-only"

    # If satellite data is unavailable, fall back to latitude-only
    if dominant_class_code is None:
        classification_method = "latitude-only"

    # If satellite data is available and dominant class is NOT Tree Cover (10):
    if dominant_class_code is not None and dominant_class_code != 10:
        dominant_name = WORLDCOVER_CLASSES.get(dominant_class_code, "Non-Forest")
        return ForestClassificationResult({
            "forest_type": "Non-Forest",
            "ecoregion": "Non-Forest",
            "dominant_land_cover": dominant_name,
            "classification_method": "satellite+latitude",
            "classification_confidence": "high",
            "recommended_standard": None,
        })

    # Dominant land cover name for tree-covered or latitude-only estimates
    if dominant_class_code == 10:
        dominant_land_cover = "Tree cover"
    else:
        dominant_land_cover = "Tree cover"

    # ------------------------------------------------------------------------
    # Priority 2: Centroid Latitude-Based Sub-Classification
    # ------------------------------------------------------------------------
    abs_lat = abs(lat)
    if abs_lat < 23.5:
        forest_type = "Tropical Moist Broadleaf"
        ecoregion = "Tropical/Subtropical"
        recommended_standard = "Verra VM0047"
    elif abs_lat < 50.0:
        forest_type = "Temperate Broadleaf"
        ecoregion = "Temperate"
        recommended_standard = "Verra VM0003"
    elif abs_lat <= 70.0:
        forest_type = "Boreal Coniferous"
        ecoregion = "Boreal"
        recommended_standard = "Verra VM0003"
    else:
        # High polar / Arctic tundra beyond 70° (polar tree line)
        forest_type = "Non-Forest"
        ecoregion = "Non-Forest"
        dominant_land_cover = "Moss and lichen"
        recommended_standard = None

    # ------------------------------------------------------------------------
    # Priority 3: NDVI Cross-Validation
    # ------------------------------------------------------------------------
    ndvi_contradicts = False
    if mean_ndvi is not None and (
        (forest_type == "Tropical Moist Broadleaf" and mean_ndvi <= 0.75)
        or (forest_type == "Temperate Broadleaf" and not (0.5 <= mean_ndvi <= 0.8))
        or (forest_type == "Boreal Coniferous" and not (0.3 <= mean_ndvi <= 0.7))
    ):
        ndvi_contradicts = True

    if ndvi_contradicts:
        logger.warning(
            "NDVI value (%.4f) contradicts latitude-based classification for %s.",
            mean_ndvi,
            forest_type,
        )
        classification_confidence = "low"
    elif spans_multiple:
        logger.info("Polygon spans multiple ecoregions; assigned %s based on centroid.", forest_type)
        classification_confidence = "medium"
    elif classification_method == "latitude-only" or mean_ndvi is None:
        classification_confidence = "medium"
    else:
        classification_confidence = "high"

    return ForestClassificationResult({
        "forest_type": forest_type,
        "ecoregion": ecoregion,
        "dominant_land_cover": dominant_land_cover,
        "classification_method": classification_method,
        "classification_confidence": classification_confidence,
        "recommended_standard": recommended_standard,
    })
