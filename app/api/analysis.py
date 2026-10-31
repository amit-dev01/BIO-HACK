"""Forest biomass and carbon analysis API endpoints."""

import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.config import Settings, get_settings
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ErrorResponse,
    PaginatedAnalysisResponse,
)
from app.services.analysis_service import AnalysisService, analysis_service
from app.utils.errors import AnalysisTimeoutError

logger = logging.getLogger("canopyai.api.analysis")

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Estimate Forest Biomass & Carbon Stock",
    description=(
        "Submit a GeoJSON Polygon boundary representing a forest area (10 to 100,000 hectares) "
        "to calculate above-ground biomass (AGBD), below-ground biomass (BGB), total carbon stock, "
        "and CO2 equivalent estimates using NASA GEDI Level 4A, ESA Sentinel-2, and IPCC Tier 1/2 formulas."
    ),
    responses={
        200: {
            "model": AnalysisResponse,
            "description": "Analysis successfully computed. In non-forest or cloud-obscured areas, valid metrics return null with warnings.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Polygon geometry invalid, area too small (< 10 ha), or area too large (> 100,000 ha)",
        },
        422: {
            "model": ErrorResponse,
            "description": "Request body schema validation failed (e.g. malformed coordinates)",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server calculation error",
        },
        503: {
            "model": ErrorResponse,
            "description": "Satellite processing or Earth Engine service unavailable",
        },
        504: {
            "model": ErrorResponse,
            "description": "Analysis computation timed out (exceeded 120 seconds)",
        },
    },
)
async def create_analysis(
    request: AnalysisRequest,
    service: AnalysisService = Depends(lambda: analysis_service),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    """Execute biomass and carbon stock estimation for the submitted polygon with 120s timeout."""
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(service.run_analysis, request),
            timeout=float(settings.analysis_timeout_seconds),
        )
    except asyncio.TimeoutError:
        logger.error("Analysis execution exceeded %s seconds", settings.analysis_timeout_seconds)
        raise AnalysisTimeoutError(
            message=f"Analysis exceeded {settings.analysis_timeout_seconds} seconds."
        )


@router.get(
    "/analyze/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Retrieve Analysis by Unique ID",
    description="Fetch a previously computed forest biomass and carbon analysis by its unique analysis UUID.",
    responses={
        200: {"model": AnalysisResponse, "description": "Analysis found and returned successfully"},
        404: {"model": ErrorResponse, "description": "Analysis ID not found"},
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
