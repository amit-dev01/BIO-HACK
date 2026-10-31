"""Pydantic data schemas and contracts for CanopyAI API."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class AnalysisType(str, Enum):
    """Supported analysis precision modes."""

    QUICK = "quick"
    DETAILED = "detailed"


class DataMode(str, Enum):
    """Identifies whether analysis results originate from simulation or active satellite observation."""

    MOCK = "mock"
    SATELLITE = "satellite"


class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon Geometry definition according to RFC 7946 specifications."""

    type: Literal["Polygon"] = Field(
        default="Polygon",
        description="GeoJSON geometry type, must be 'Polygon'",
    )
    coordinates: List[List[List[float]]] = Field(
        ...,
        description=(
            "Linear rings forming the polygon. The first ring is the exterior boundary. "
            "Each ring must have at least 4 positions [longitude, latitude] with the first and last position identical."
        ),
        examples=[
            [
                [
                    [-60.05, -3.12],
                    [-60.00, -3.12],
                    [-60.00, -3.16],
                    [-60.05, -3.16],
                    [-60.05, -3.12],
                ]
            ]
        ],
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon_coordinates(cls, coords: List[List[List[float]]]) -> List[List[List[float]]]:
        """Validate structure, completeness, coordinates bounds, and closure of the polygon."""
        if not coords or not isinstance(coords, list):
            raise ValueError("Polygon coordinates must be a non-empty list of linear rings")

        for ring_idx, ring in enumerate(coords):
            if not isinstance(ring, list) or len(ring) < 4:
                raise ValueError(
                    f"Linear ring {ring_idx} must contain at least 4 positions (got {len(ring) if isinstance(ring, list) else 'non-list'})"
                )

            # Validate each coordinate pair
            for pt_idx, pt in enumerate(ring):
                if not isinstance(pt, (list, tuple)) or len(pt) < 2:
                    raise ValueError(f"Ring {ring_idx}, coordinate {pt_idx} must have at least 2 elements [lon, lat]")
                lon, lat = pt[0], pt[1]
                if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
                    raise ValueError(f"Coordinates must be numeric: got ({lon}, {lat})")
                if not (-180.0 <= lon <= 180.0):
                    raise ValueError(f"Longitude {lon} out of range [-180, 180]")
                if not (-90.0 <= lat <= 90.0):
                    raise ValueError(f"Latitude {lat} out of range [-90, 90]")

            # Validate closure (first point equals last point)
            first_pt, last_pt = ring[0], ring[-1]
            if abs(first_pt[0] - last_pt[0]) > 1e-7 or abs(first_pt[1] - last_pt[-1]) > 1e-7:
                raise ValueError(
                    f"Linear ring {ring_idx} is not closed: first point {first_pt[:2]} != last point {last_pt[:2]}"
                )

        return coords


class AnalysisRequest(BaseModel):
    """Inbound request payload for triggering forest carbon and biomass analysis."""

    polygon: GeoJSONPolygon = Field(
        ...,
        description="GeoJSON Polygon boundary defining the target forest evaluation region",
    )
    analysis_type: AnalysisType = Field(
        default=AnalysisType.QUICK,
        description="Depth of analysis: 'quick' for rapid estimates or 'detailed' for multi-sensor integration",
    )
    data_sources: List[str] = Field(
        default_factory=lambda: ["sentinel-2", "gedi"],
        description="List of selected satellite datasets or sensors (e.g. ['sentinel-2', 'gedi', 'landsat'])",
        examples=[["sentinel-2", "gedi"]],
    )


class AnalysisResponse(BaseModel):
    """Complete forest biomass and carbon storage analysis response contract.

    Units:
    - Area: hectares (ha)
    - Biomass: tonnes per hectare (t/ha)
    - Carbon: tonnes of carbon per hectare (t/ha)
    - CO2e: tonnes of CO2 equivalent (t CO2e)
    """

    analysis_id: str = Field(..., description="Unique analysis execution identifier (UUID4)")
    timestamp: datetime = Field(..., description="Timestamp of analysis generation (UTC ISO 8601)")
    polygon: GeoJSONPolygon = Field(..., description="The evaluated GeoJSON Polygon boundary")
    area_ha: float = Field(..., description="Surface area of the evaluated polygon in hectares (ha)")
    forest_type: Optional[str] = Field(None, description="Dominant forest classification type")
    ecoregion: Optional[str] = Field(None, description="Terrestrial ecoregion classification")
    canopy_cover_pct: Optional[float] = Field(None, description="Estimated canopy cover percentage (0-100%)")
    mean_canopy_height_m: Optional[float] = Field(None, description="Estimated mean canopy height in meters (m)")
    agb_t_per_ha: Optional[float] = Field(None, description="Above-ground biomass density (tonnes/ha)")
    bgb_t_per_ha: Optional[float] = Field(None, description="Below-ground biomass density (tonnes/ha)")
    total_biomass_t_per_ha: Optional[float] = Field(None, description="Total biomass density (AGB + BGB) in tonnes/ha")
    carbon_fraction: Optional[float] = Field(None, description="Carbon fraction factor (IPCC default ~0.47)")
    carbon_t_per_ha: Optional[float] = Field(None, description="Carbon density in tonnes of carbon/ha")
    co2e_t_per_ha: Optional[float] = Field(None, description="Carbon dioxide equivalent density in tonnes CO2e/ha")
    total_co2e: Optional[float] = Field(None, description="Total estimated CO2e stock in tonnes across entire area")
    confidence_score: Optional[float] = Field(None, description="Model confidence score between 0.0 and 1.0")
    confidence_label: Optional[str] = Field(None, description="Human-readable confidence grade: High, Moderate, Low")
    confidence_interval_pct: Optional[float] = Field(None, description="Estimated uncertainty margin percentage (±%)")
    ndvi_trend: Optional[str] = Field(None, description="Normalized Difference Vegetation Index trend: stable, increasing, decreasing")
    data_sources: List[str] = Field(..., description="Satellite and sensor datasets used during computation")
    processing_time_seconds: float = Field(..., description="Server-side processing runtime in seconds")
    data_mode: DataMode = Field(..., description="Indicates whether result is 'mock' (simulated) or 'satellite'")
    disclaimer: str = Field(
        default="Scientific ecological estimation for monitoring purposes. Does not constitute verified or certified carbon credits.",
        description="Regulatory disclaimer on carbon estimates",
    )


class PaginatedAnalysisResponse(BaseModel):
    """Paginated list of previous forest analyses."""

    items: List[AnalysisResponse] = Field(..., description="List of completed analyses for the current page")
    total: int = Field(..., description="Total count of recorded analyses")
    page: int = Field(..., description="Current page number (1-indexed)")
    limit: int = Field(..., description="Page limit / size")
    total_pages: int = Field(..., description="Total number of pages available")


class HealthResponse(BaseModel):
    """System health and operational status response."""

    status: str = Field(default="ok", description="Operational status ('ok')")
    version: str = Field(..., description="Active API version")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")
    mock_mode: bool = Field(..., description="True if operating in simulated mock mode without satellite credentials")
    environment: str = Field(default="development", description="Runtime environment")


class ErrorResponse(BaseModel):
    """Standardized error contract for all API responses."""

    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation of the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional diagnostic details or field errors")
