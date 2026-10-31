"""Geospatial module for polygon validation, geodesic area, centroid, and bounding box calculations.

Part of CanopyAI forest carbon estimation platform.
Designed for WGS84 geographic coordinate reference system (EPSG:4326).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import shapely.errors
from pyproj import Geod
from shapely.geometry import Polygon

# Platform operational limits
MIN_SUPPORTED_AREA_HA: float = 10.0
MAX_SUPPORTED_AREA_HA: float = 100_000.0

# WGS84 Geoid for ellipsoidal geodesic calculations
_WGS84_GEOD = Geod(ellps="WGS84")

# Coordinate bounds
_MIN_LON = -180.0
_MAX_LON = 180.0
_MIN_LAT = -90.0
_MAX_LAT = 90.0


def _is_valid_coord_pair(coord: Any) -> bool:
    """Validate that a coordinate is an [x/lon, y/lat] numeric pair within valid WGS84 bounds."""
    if not isinstance(coord, (list, tuple)) or len(coord) < 2:
        return False
    lon, lat = coord[0], coord[1]
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        return False
    if math.isnan(lon) or math.isnan(lat) or math.isinf(lon) or math.isinf(lat):
        return False
    if not (_MIN_LON <= lon <= _MAX_LON):
        return False
    return _MIN_LAT <= lat <= _MAX_LAT


def _extract_rings_from_input(
    polygon: Any,
) -> tuple[list[list[float]], list[list[list[float]]]] | None:
    """Extract exterior and interior coordinate rings from various input representations.

    Supports:
    - GeoJSON Feature dict: {"type": "Feature", "geometry": {"type": "Polygon", ...}}
    - GeoJSON Polygon dict: {"type": "Polygon", "coordinates": [[[lon, lat], ...], ...]}
    - GeoJSON Polygon coordinate list: [[[lon, lat], ...], ...]
    - Single ring coordinate list: [[lon, lat], ...]
    - Shapely Polygon object

    Returns:
        (exterior_coords, interior_coords_list) or None if format is unparseable.
    """
    if polygon is None:
        return None

    # Handle Shapely Polygon
    if isinstance(polygon, Polygon):
        if polygon.is_empty or not polygon.is_valid:
            return None
        exterior = [list(pt) for pt in polygon.exterior.coords]
        interiors = [[list(pt) for pt in interior.coords] for interior in polygon.interiors]
        return exterior, interiors

    # Handle GeoJSON Feature
    if isinstance(polygon, dict) and polygon.get("type") == "Feature":
        polygon = polygon.get("geometry")

    # Handle GeoJSON Geometry dictionary
    if isinstance(polygon, dict):
        geom_type = polygon.get("type")
        if geom_type != "Polygon":
            return None
        coords = polygon.get("coordinates")
        if not isinstance(coords, (list, tuple)) or len(coords) == 0:
            return None
        exterior = coords[0]
        interiors = list(coords[1:]) if len(coords) > 1 else []
        return exterior, interiors

    # Handle raw coordinate lists / tuples
    if isinstance(polygon, (list, tuple)):
        if len(polygon) == 0:
            return None
        first_elem = polygon[0]
        # Check if single ring: [[lon, lat], [lon, lat], ...]
        if isinstance(first_elem, (list, tuple)) and len(first_elem) >= 2 and isinstance(first_elem[0], (int, float)):
            return list(polygon), []
        # Check if nested rings: [[[lon, lat], ...], ...]
        if isinstance(first_elem, (list, tuple)) and len(first_elem) > 0 and isinstance(first_elem[0], (list, tuple)):
            exterior = list(polygon[0])
            interiors = [list(ring) for ring in polygon[1:]] if len(polygon) > 1 else []
            return exterior, interiors

    return None


def _rings_to_shapely(
    exterior: Sequence[Sequence[float]],
    interiors: Sequence[Sequence[Sequence[float]]],
) -> Polygon | None:
    """Validate ring rules and build a Shapely Polygon."""
    # Validate exterior ring length: must have at least 4 coordinates (3 distinct + closed point)
    if not isinstance(exterior, (list, tuple)) or len(exterior) < 4:
        return None

    # Check closed ring condition: first coordinate must match last coordinate
    first_pt = exterior[0]
    last_pt = exterior[-1]
    if len(first_pt) < 2 or len(last_pt) < 2:
        return None
    if not (math.isclose(first_pt[0], last_pt[0], abs_tol=1e-9) and math.isclose(first_pt[1], last_pt[1], abs_tol=1e-9)):
        return None

    # Validate coordinate ranges for all exterior vertices
    for pt in exterior:
        if not _is_valid_coord_pair(pt):
            return None

    # Check that there are at least 3 distinct vertices in the exterior ring
    distinct_pts = {(round(pt[0], 9), round(pt[1], 9)) for pt in exterior}
    if len(distinct_pts) < 3:
        return None

    # Validate interiors if present
    validated_interiors = []
    for interior in interiors:
        if not isinstance(interior, (list, tuple)) or len(interior) < 4:
            return None
        if not (math.isclose(interior[0][0], interior[-1][0], abs_tol=1e-9) and math.isclose(interior[0][1], interior[-1][1], abs_tol=1e-9)):
            return None
        for pt in interior:
            if not _is_valid_coord_pair(pt):
                return None
        if len({(round(pt[0], 9), round(pt[1], 9)) for pt in interior}) < 3:
            return None
        validated_interiors.append(interior)

    try:
        poly = Polygon(exterior, validated_interiors)
    except (ValueError, TypeError, shapely.errors.GEOSException):
        return None

    # Verify geometry validity (OGC rules: non-self-intersecting, non-empty, simple exterior)
    if not poly.is_valid or poly.is_empty:
        return None

    if not poly.exterior.is_simple:
        return None

    for hole in poly.interiors:
        if not hole.is_simple:
            return None

    return poly


def parse_polygon(polygon: Any) -> Polygon:
    """Parse and validate any supported polygon input into a valid Shapely Polygon.

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, coordinate list, or Shapely Polygon.

    Returns:
        Valid shapely.geometry.Polygon.

    Raises:
        ValueError: If geometry is unparseable, unclosed, self-intersecting, or out of coordinate bounds.
        TypeError: If input polygon is None or an unsupported type.
    """
    if polygon is None:
        raise TypeError("Polygon input cannot be None.")

    extracted = _extract_rings_from_input(polygon)
    if extracted is None:
        raise ValueError("Could not extract coordinate rings from input geometry.")

    exterior, interiors = extracted
    poly = _rings_to_shapely(exterior, interiors)
    if poly is None:
        raise ValueError("Invalid polygon geometry: must be a closed, non-self-intersecting polygon with valid WGS84 coordinates.")

    return poly


def validate_polygon(polygon: Any, check_area_limits: bool = False) -> bool:
    """Validate a GeoJSON polygon geometry.

    Checks:
    - Valid polygon geometry
    - Closed polygon boundaries (first and last coordinate match)
    - Correct longitude [-180, 180] and latitude [-90, 90] ranges
    - Non-self-intersecting polygon
    - Optional area bounds validation (10 to 100,000 hectares)

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, coordinate sequence, or Shapely Polygon.
        check_area_limits: When True, also checks if area is within [10, 100,000] ha.

    Returns:
        True if all validation checks pass, False otherwise.
    """
    if polygon is None:
        return False

    try:
        poly = parse_polygon(polygon)
        if poly is None or not poly.is_valid or poly.is_empty:
            return False

        if check_area_limits:
            area_ha = calculate_area_ha(poly)
            if not is_area_supported(area_ha):
                return False

        return True
    except (ValueError, TypeError, KeyError, IndexError):
        return False


def is_area_supported(area_ha: float) -> bool:
    """Check if the polygon area falls within platform operational limits (10 to 100,000 ha).

    Args:
        area_ha: Area in hectares.

    Returns:
        True if MIN_SUPPORTED_AREA_HA <= area_ha <= MAX_SUPPORTED_AREA_HA, False otherwise.
    """
    if area_ha is None or not isinstance(area_ha, (int, float)):
        return False
    if math.isnan(area_ha) or math.isinf(area_ha):
        return False
    return MIN_SUPPORTED_AREA_HA <= area_ha <= MAX_SUPPORTED_AREA_HA


def validate_polygon_area(polygon: Any) -> bool:
    """Validate both polygon geometry and operational area constraints (10 to 100,000 ha).

    Args:
        polygon: Polygon representation.

    Returns:
        True if valid geometry and area is between 10 ha and 100,000 ha.
    """
    return validate_polygon(polygon, check_area_limits=True)


def calculate_area_ha(polygon: Any) -> float:
    """Calculate the geodesic area of a polygon in hectares on the WGS84 ellipsoid.

    Geodesic calculation accounts for ellipsoidal curvature, providing
    high accuracy globally without projection distortion.

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, coordinate list, or Shapely Polygon.

    Returns:
        Area in hectares (float).

    Raises:
        ValueError: If polygon geometry is invalid or unparseable.
        TypeError: If polygon is None.
    """
    poly = parse_polygon(polygon)

    # Ellipsoidal geodesic calculation on WGS84
    exterior_area, _ = _WGS84_GEOD.geometry_area_perimeter(Polygon(poly.exterior))
    net_m2 = abs(exterior_area)

    # Subtract interior holes if present
    for interior in poly.interiors:
        hole_area, _ = _WGS84_GEOD.geometry_area_perimeter(Polygon(interior))
        net_m2 -= abs(hole_area)

    # Convert square meters to hectares: 1 ha = 10,000 m²
    area_ha = max(0.0, net_m2) / 10_000.0
    return float(area_ha)


def get_centroid(polygon: Any) -> tuple[float, float]:
    """Calculate the geographic centroid of a polygon.

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, coordinate list, or Shapely Polygon.

    Returns:
        Tuple of (longitude, latitude) as floats.

    Raises:
        ValueError: If polygon geometry is invalid or unparseable.
        TypeError: If polygon is None.
    """
    poly = parse_polygon(polygon)
    centroid = poly.centroid
    return (float(centroid.x), float(centroid.y))


def get_bounding_box(polygon: Any) -> tuple[float, float, float, float]:
    """Calculate the bounding box of a polygon in standard WGS84 bounds.

    Args:
        polygon: GeoJSON Polygon dict, Feature dict, coordinate list, or Shapely Polygon.

    Returns:
        Tuple of (min_longitude, min_latitude, max_longitude, max_latitude) as floats.

    Raises:
        ValueError: If polygon geometry is invalid or unparseable.
        TypeError: If polygon is None.
    """
    poly = parse_polygon(polygon)
    minx, miny, maxx, maxy = poly.bounds
    return (float(minx), float(miny), float(maxx), float(maxy))
