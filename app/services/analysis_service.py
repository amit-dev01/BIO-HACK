"""Analysis service interface orchestrating forest carbon and biomass workflows.

Connects the API boundary to estimation pipelines. Operates in mock mode currently,
and designed for seamless integration with Developer 1's satellite observation modules
(app.core.* and app.utils.geo) once delivered.
"""

import math
from typing import Optional
from app.config import Settings, get_settings
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    GeoJSONPolygon,
    PaginatedAnalysisResponse,
)
from app.services.mock_service import (
    MockAnalysisService,
    calculate_polygon_area_ha,
    mock_repository,
)
from app.utils.errors import (
    AnalysisNotFoundError,
    InvalidPolygonError,
    PolygonTooLargeError,
    PolygonTooSmallError,
    SatelliteUnavailableError,
)


class AnalysisService:
    """Service orchestrating the complete carbon assessment workflow.

    Workflow phases:
    1. Receive polygon
    2. Validate request structure
    3. Validate polygon geometry
    4. Calculate area and evaluate size bounds
    5. Retrieve satellite observations (Dev 1 module)
    6. Calculate biomass (Dev 1 module)
    7. Calculate carbon stock (Dev 1 module)
    8. Evaluate data quality & confidence
    9. Assemble analysis response
    10. Save analysis to persistence repository
    11. Return response
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        mock_service: Optional[MockAnalysisService] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.mock_service = mock_service or MockAnalysisService(repository=mock_repository)

    def validate_polygon_geometry(self, polygon: GeoJSONPolygon) -> None:
        """Validate geometric properties of the GeoJSON polygon.

        Checks coordinate structure, closure, and validity beyond basic schema checks.
        """
        if polygon.type != "Polygon":
            raise InvalidPolygonError(message=f"Expected geometry type 'Polygon', received '{polygon.type}'")

        if not polygon.coordinates or len(polygon.coordinates) == 0:
            raise InvalidPolygonError(message="Polygon must contain at least one linear ring")

        exterior_ring = polygon.coordinates[0]
        if len(exterior_ring) < 4:
            raise InvalidPolygonError(
                message=f"Exterior ring must contain at least 4 coordinate pairs, got {len(exterior_ring)}"
            )

        # Check closure
        first, last = exterior_ring[0], exterior_ring[-1]
        if abs(first[0] - last[0]) > 1e-7 or abs(first[1] - last[1]) > 1e-7:
            raise InvalidPolygonError(message="Polygon exterior ring is not closed (first point != last point)")

    def calculate_and_validate_area(self, polygon: GeoJSONPolygon) -> float:
        """Calculate the geodesic area in hectares and enforce boundary limits."""
        area_ha = calculate_polygon_area_ha(polygon.coordinates)

        if area_ha <= 1e-12 or math.isnan(area_ha):
            raise InvalidPolygonError(message="Computed polygon area is zero or degenerate")

        if area_ha < self.settings.min_polygon_area_ha:
            raise PolygonTooSmallError(
                message=(
                    f"Polygon area of {area_ha:.4f} ha is below the minimum threshold "
                    f"of {self.settings.min_polygon_area_ha} hectares"
                ),
                area_ha=area_ha,
                min_ha=self.settings.min_polygon_area_ha,
            )

        if area_ha > self.settings.max_polygon_area_ha:
            raise PolygonTooLargeError(
                message=(
                    f"Polygon area of {area_ha:.2f} ha exceeds the maximum allowable threshold "
                    f"of {self.settings.max_polygon_area_ha} hectares"
                ),
                area_ha=area_ha,
                max_ha=self.settings.max_polygon_area_ha,
            )

        return area_ha

    def run_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute the analysis workflow for the provided forest boundary."""
        # 1. Receive polygon
        # 2. Validate request structure (done via Pydantic)
        # 3. Validate polygon geometry
        self.validate_polygon_geometry(request.polygon)

        # 4. Calculate area and validate against bounds
        area_ha = self.calculate_and_validate_area(request.polygon)

        # 5-11. Execution dispatch
        if self.settings.mock_mode:
            # Delegate to mock service for simulated pipeline
            return self.mock_service.generate_analysis(request, computed_area_ha=area_ha)

        # Live satellite path: designed for Developer 1 integration
        try:
            # Future integration hook:
            # from app.core.satellite import fetch_satellite_data
            # from app.core.biomass import calculate_forest_biomass
            # ...
            raise NotImplementedError("Developer 1 satellite pipeline is not yet attached")
        except (ImportError, NotImplementedError):
            raise SatelliteUnavailableError(
                message="Live satellite pipeline is undergoing integration. Please run in mock mode (MOCK_MODE=True)."
            )

    def get_analysis_by_id(self, analysis_id: str) -> AnalysisResponse:
        """Retrieve a previously generated analysis by its unique ID."""
        analysis = self.mock_service.repository.get_by_id(analysis_id)
        if not analysis:
            raise AnalysisNotFoundError(analysis_id=analysis_id)
        return analysis

    def list_analyses(self, page: int = 1, limit: int = 10) -> PaginatedAnalysisResponse:
        """Retrieve paginated analyses recorded in the system."""
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        items, total = self.mock_service.repository.list(page=page, limit=limit)
        total_pages = math.ceil(total / limit) if total > 0 else 1

        return PaginatedAnalysisResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )


# Global service instance
analysis_service = AnalysisService()
