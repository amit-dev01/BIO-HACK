"""Forest classification and canopy cover extraction module for CanopyAI.

Phase 2 Forest Biome Classification:
Classifies the dominant forest type/biome for an evaluation polygon to support
biome-specific root-to-shoot ratios in biomass calculations.

Standard Biome Categories (compatible with app.core.biomass):
  - "Tropical Moist Broadleaf"
  - "Temperate Broadleaf"
  - "Boreal Coniferous"
  - "Other"
"""

from __future__ import annotations

import logging
from typing import Any

from app.utils.geo import get_centroid, parse_polygon

logger = logging.getLogger("canopyai.forest_classifier")


def _classify_biome_by_latitude(latitude: float) -> str:
    """Classify standard forest biome from geographic latitude.

    Standard global latitudinal forest zonation:
      - |lat| <= 23.5°: Tropical (Tropical Moist Broadleaf)
      - 23.5° < |lat| <= 50.0°: Temperate (Temperate Broadleaf)
      - 50.0° < |lat| <= 70.0°: Boreal (Boreal Coniferous)
      - |lat| > 70.0°: Polar / Tundra / Non-forest (Other)
    """
    abs_lat = abs(latitude)
    if abs_lat <= 23.5:
        return "Tropical Moist Broadleaf"
    if abs_lat <= 50.0:
        return "Temperate Broadleaf"
    if abs_lat <= 70.0:
        return "Boreal Coniferous"
    return "Other"


def classify_forest_type(polygon: Any) -> str:
    """Classify the dominant forest biome/type for a given polygon.

    Uses Earth Engine land cover datasets (e.g. ESA WorldCover / Dynamic World)
    when active and available, paired with geographic coordinate screening to
    assign one of the standard biome categories.

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, Shapely Polygon, or coordinates.

    Returns:
        One of:
          - "Tropical Moist Broadleaf"
          - "Temperate Broadleaf"
          - "Boreal Coniferous"
          - "Other"

    Raises:
        TypeError: If polygon is None.
        ValueError: If polygon geometry is invalid.
    """
    if polygon is None:
        raise TypeError("Polygon input cannot be None.")

    # Validate geometry
    if hasattr(polygon, "model_dump"):
        polygon = polygon.model_dump()

    poly = parse_polygon(polygon)
    lon, lat = get_centroid(poly)

    # Base classification by geographic biome
    biome = _classify_biome_by_latitude(lat)

    # Attempt satellite land-cover verification via Earth Engine if initialized
    try:
        import ee

        if hasattr(ee, "data") and hasattr(ee.data, "is_initialized") and ee.data.is_initialized():
            ee_geom = ee.Geometry.Point([lon, lat])
            # Query ESA WorldCover (Class 10 = Tree cover)
            worldcover = ee.Image("ESA/WorldCover/v100/2020")
            sampled = worldcover.reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=ee_geom,
                scale=10,
            ).getInfo()

            if sampled and "Map" in sampled:
                cover_code = sampled["Map"]
                # 10 is Tree cover. If clearly non-tree (e.g., 50=Built-up, 60=Bare, 80=Water), assign "Other"
                if cover_code is not None and cover_code not in (10, 20, 30):
                    return "Other"

    except Exception as exc:  # noqa: BLE001
        logger.debug("Satellite land cover lookup fell back to geographic biome: %s", exc)

    return biome
