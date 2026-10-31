"""Forest biomass and carbon analysis API endpoints."""

from typing import Optional
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
    summary="List Analyses History (Paginated)",
    description="Retrieve a paginated list of all forest analyses recorded in Supabase or session memory, sorted newest first.",
    responses={
        200: {"model": PaginatedAnalysisResponse, "description": "Paginated list of analyses"},
    },
)
async def list_analyses(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items per page (max: 100)"),
    offset: int = Query(default=0, ge=0, description="Offset index (0-indexed)"),
    page: Optional[int] = Query(default=None, ge=1, description="Optional page number (1-indexed, for backward compatibility)"),
    service: AnalysisService = Depends(lambda: analysis_service),
) -> PaginatedAnalysisResponse:
    """List historical analyses with pagination."""
    return service.list_analyses(limit=limit, offset=offset, page=page)
