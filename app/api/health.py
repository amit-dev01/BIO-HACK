"""Health check and diagnostic API endpoints."""

from datetime import datetime, timezone
import logging
import time
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.schemas import HealthResponse, ServiceHealth, SystemHealth
from app.services.database_service import DatabaseService, database_service

logger = logging.getLogger("canopyai.health")

router = APIRouter(tags=["Health"])

# Module-level tracking for server start timestamp
SERVER_BOOT_TIME: float = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health & Diagnostic Status",
    description=(
        "Check backend operational status ('ok' or 'degraded'), active API version, "
        "uptime, system resource metrics (CPU/RAM), Earth Engine connectivity, and database status."
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
    """Return system health status, resource utilization, and external service diagnostics."""
    now_utc = datetime.now(timezone.utc)
    uptime = max(0.0, round(time.time() - SERVER_BOOT_TIME, 2))

    # 1. Determine Earth Engine connectivity status
    if settings.mock_mode:
        ee_status = "mock"
    else:
        try:
            import ee
            if hasattr(ee, "data") and hasattr(ee.data, "is_initialized") and ee.data.is_initialized():
                ee_status = "connected"
            else:
                ee_status = "error"
        except Exception as ee_exc:
            logger.debug("Earth Engine health evaluation caught error: %s", ee_exc)
            ee_status = "error"

    # 2. Determine Supabase Database status
    if db_service.is_connected:
        db_status = "connected"
    elif settings.mock_mode:
        db_status = "connected"  # Operating in healthy in-memory mock mode
    else:
        db_status = "error"

    # 3. Overall operational status: degraded if any non-mock service is in error
    is_degraded = (ee_status == "error") or (db_status == "error")
    overall_status = "degraded" if is_degraded else "ok"

    # 4. Host system resource telemetry (CPU/Memory)
    try:
        import psutil
        cpu_val = float(psutil.cpu_percent(interval=None))
        mem_val = float(psutil.virtual_memory().percent)
    except Exception as sys_exc:
        logger.debug("System metrics telemetry unavailable: %s", sys_exc)
        cpu_val = 0.0
        mem_val = 0.0

    services_dict = {
        "earth_engine": ServiceHealth(status=ee_status, last_check=now_utc),
        "database": ServiceHealth(status=db_status, last_check=now_utc),
    }

    system_metrics = SystemHealth(cpu_percent=cpu_val, memory_percent=mem_val)

    # Backward compatibility attributes for Phase 1-4 tests
    legacy_ee = "mock" if settings.mock_mode else ("connected" if ee_status == "connected" else "disconnected")
    legacy_db = "connected" if db_service.is_connected else "disconnected"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        timestamp=now_utc,
        uptime_seconds=uptime,
        services=services_dict,
        system=system_metrics,
        mock_mode=settings.mock_mode,
        environment=settings.environment,
        earth_engine=legacy_ee,
        database=legacy_db,
    )
