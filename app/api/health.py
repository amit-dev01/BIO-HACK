"""Health check and diagnostic API endpoints."""

from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.schemas import HealthResponse
from app.services.database_service import DatabaseService, database_service

logger = logging.getLogger("canopyai.health")

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health & Diagnostic Status",
    description=(
        "Check backend operational status, active API version, current server timestamp, "
        "mock mode configuration, Earth Engine connectivity, and database status."
    ),
    responses={
        200: {
            "model": HealthResponse,
            "description": "System health and operational diagnostic metrics",
        }
    },
)
async def check_health(
    settings: Settings = Depends(get_settings),
    db_service: DatabaseService = Depends(lambda: database_service),
) -> HealthResponse:
    """Return system health status and configuration details."""
    # Determine Earth Engine connectivity status
    if settings.mock_mode:
        ee_status = "mock"
    else:
        try:
            import ee
            if hasattr(ee, "data") and hasattr(ee.data, "is_initialized") and ee.data.is_initialized():
                ee_status = "connected"
            else:
                ee_status = "disconnected"
        except Exception:
            ee_status = "disconnected"

    # Determine Supabase Database status
    db_status = "connected" if db_service.is_connected else "disconnected"

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        mock_mode=settings.mock_mode,
        environment=settings.environment,
        earth_engine=ee_status,
        database=db_status,
    )
