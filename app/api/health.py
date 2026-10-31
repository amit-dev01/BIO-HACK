"""Health check and diagnostic API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.config import Settings, get_settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Check backend operational status, active API version, current server timestamp, and mock mode configuration.",
)
async def check_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return system health status and configuration details."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        mock_mode=settings.mock_mode,
        environment=settings.environment,
    )
