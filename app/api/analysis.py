"""Forest biomass and carbon analysis API endpoints."""

from fastapi import APIRouter, Depends, Query, status
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse,
    PaginatedAnalysisResponse,
)
from app.services.analysis_service import AnalysisService, analysis_service

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger Forest Carbon Analysis",
    description=(
        "Submit a GeoJSON Polygon defining a forest area to compute above-ground biomass, "
        "below-ground biomass, total carbon stock, and CO2 equivalent estimates."
    ),
    responses={
        200: {"model": AnalysisResponse, "description": "Analysis successfully computed"},
        400: {"model": ErrorResponse, "description": "Invalid polygon or boundary constraints violated"},
        422: {"model": ErrorResponse, "description": "Request schema validation failed"},
        500: {"model": ErrorResponse, "description": "Internal server processing error"},
        503: {"model": ErrorResponse, "description": "Satellite processing service unavailable"},
    },
)
async def create_analysis(
    request: AnalysisRequest,
    service: AnalysisService = Depends(lambda: analysis_service),
) -> AnalysisResponse:
    """Execute biomass and carbon stock estimation for the submitted polygon."""
    return service.run_analysis(request)


@router.get(
    "/analyze/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Retrieve Analysis by ID",
    description="Fetch a previously computed forest biomass and carbon analysis by its unique analysis ID.",
    responses={
        200: {"model": AnalysisResponse, "description": "Analysis found and returned"},
        404: {"model": ErrorResponse, "description": "Analysis not found"},
    },
)
async def get_analysis_by_id(
    analysis_id: str,
    service: AnalysisService = Depends(lambda: analysis_service),
) -> AnalysisResponse:
    """Retrieve an existing analysis by ID."""
    return service.get_analysis_by_id(analysis_id)


@router.get(
    "/analyses",
    response_model=PaginatedAnalysisResponse,
    summary="List Analyses (Paginated)",
    description="Retrieve a paginated list of all forest analyses recorded during the active session.",
    responses={
        200: {"model": PaginatedAnalysisResponse, "description": "Paginated list of analyses"},
    },
)
async def list_analyses(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    service: AnalysisService = Depends(lambda: analysis_service),
) -> PaginatedAnalysisResponse:
    """List historical analyses with pagination."""
    return service.list_analyses(page=page, limit=limit)
