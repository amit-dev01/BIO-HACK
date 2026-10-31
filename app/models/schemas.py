"""Pydantic data schemas and contracts for CanopyAI API."""

from datetime import datetime
from enum import Enum
import math
from typing import Any, Dict, List, Literal, Optional, Union
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
            if abs(first_pt[0] - last_pt[0]) > 1e-7 or abs(first_pt[1] - last_pt[1]) > 1e-7:
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
    canopy_data_available: Optional[bool] = Field(None, description="Indicates if canopy cover or height data was available")
    mean_canopy_height_m: Optional[float] = Field(None, description="Estimated mean canopy height in meters (m)")
    agb_t_per_ha: Optional[float] = Field(None, description="Above-ground biomass density (tonnes/ha)")
    bgb_t_per_ha: Optional[float] = Field(None, description="Below-ground biomass density (tonnes/ha)")
    total_biomass_t_per_ha: Optional[float] = Field(None, description="Total biomass density (AGB + BGB) in tonnes/ha")
    carbon_fraction: Optional[float] = Field(None, description="Carbon fraction factor (IPCC default ~0.47)")
    carbon_t_per_ha: Optional[float] = Field(None, description="Carbon density in tonnes of carbon/ha")
    co2e_t_per_ha: Optional[float] = Field(None, description="Carbon dioxide equivalent density in tonnes CO2e/ha")
    total_co2e: Optional[float] = Field(None, description="Total estimated CO2e stock in tonnes across entire area")
    confidence_score: Optional[float] = Field(None, description="Model confidence score between 0.0 and 1.0 (or 0-100)")
    confidence_label: Optional[str] = Field(None, description="Human-readable confidence grade: High, Moderate, Low")
    confidence_interval_pct: Optional[float] = Field(None, description="Estimated uncertainty margin percentage (±%)")
    ndvi_trend: Optional[Union[str, List[Dict[str, Any]]]] = Field(
        None,
        description="NDVI vegetation health trend: string classification or quarterly time series",
    )
    data_sources: List[str] = Field(..., description="Satellite and sensor datasets used during computation")
    processing_time_seconds: int = Field(..., description="Server-side processing runtime in seconds (integer)")
    data_mode: Union[DataMode, str] = Field(..., description="Indicates whether result is 'mock' (simulated) or 'satellite'")
    dominant_land_cover: Optional[str] = Field(None, description="Dominant land cover class (e.g. Tree cover, Non-Forest)")
    classification_method: Optional[str] = Field(None, description="Method used to classify forest type / biome")
    classification_confidence: Optional[str] = Field(None, description="Confidence assessment for land cover classification")
    recommended_standard: Optional[str] = Field(None, description="Recommended carbon estimation standard (e.g. IPCC Tier 1/2)")
    data_warnings: List[str] = Field(default_factory=list, description="Warnings encountered during satellite retrieval")
    validation_summary: Optional[Dict[str, Any]] = Field(None, description="Geometric validation summary")
    uncertainty: Optional[Dict[str, Any]] = Field(None, description="Empirical uncertainty metrics")
    disclaimer: str = Field(
        default="Scientific ecological estimation for monitoring purposes. Does not constitute verified or certified carbon credits.",
        description="Regulatory disclaimer on carbon estimates",
    )

    @field_validator("processing_time_seconds", mode="before")
    @classmethod
    def coerce_processing_time(cls, v: Any) -> int:
        """Coerce float/string processing time to integer seconds."""
        if isinstance(v, (float, int)):
            return int(round(v))
        if isinstance(v, str):
            try:
                return int(round(float(v)))
            except ValueError:
                pass
        return v


class AnalysisSummary(BaseModel):
    """Summary record for analysis history listings."""

    analysis_id: str = Field(..., description="Unique analysis execution identifier")
    timestamp: datetime = Field(..., description="Timestamp of analysis creation (UTC ISO 8601)")
    area_ha: float = Field(..., description="Evaluated forest area in hectares")
    total_co2e: Optional[float] = Field(None, description="Estimated total carbon dioxide equivalent in tonnes")
    forest_type: Optional[str] = Field(None, description="Dominant forest classification type")
    confidence_score: Optional[int] = Field(None, description="Model confidence score as integer between 0 and 100")
    status: str = Field(default="complete", description="Analysis execution status: 'complete' or 'failed'")


class PaginatedAnalysisResponse(BaseModel):
    """Paginated response containing list of analysis summaries."""

    total: int = Field(..., description="Total count of recorded analyses")
    limit: int = Field(..., description="Page limit / size")
    offset: int = Field(default=0, description="Offset / starting index (0-indexed)")
    analyses: List[AnalysisSummary] = Field(default_factory=list, description="List of analysis summaries")

    # Backward compatibility attributes for Phase 1 API consumers
    items: Optional[List[Any]] = Field(default=None, description="Backward compatible alias for analyses")
    page: Optional[int] = Field(default=1, description="Page number (1-indexed)")
    total_pages: Optional[int] = Field(default=1, description="Total number of pages available")

    def model_post_init(self, __context: Any) -> None:
        if self.items is None:
            self.items = self.analyses
        if self.limit > 0:
            if self.page is None or self.page == 1:
                self.page = (self.offset // self.limit) + 1
            self.total_pages = max(1, math.ceil(self.total / self.limit)) if self.total > 0 else 1


AnalysisHistoryResponse = PaginatedAnalysisResponse


class HealthResponse(BaseModel):
    """System health and operational status response."""

    status: str = Field(default="ok", description="Operational status ('ok')")
    version: str = Field(..., description="Active API version")
    timestamp: datetime = Field(..., description="Current server UTC timestamp")
    mock_mode: bool = Field(..., description="True if operating in simulated mock mode without satellite credentials")
    environment: str = Field(default="development", description="Runtime environment")
    earth_engine: str = Field(default="mock", description="'connected', 'disconnected', or 'mock'")
    database: str = Field(default="disconnected", description="'connected' or 'disconnected'")


class ErrorResponse(BaseModel):
    """Standardized error contract for all API responses."""

    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation of the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional diagnostic details or field errors")
