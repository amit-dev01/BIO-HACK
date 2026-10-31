"""FastAPI application entrypoint for CanopyAI backend API service."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import analysis, health, reports
from app.config import get_settings
from app.utils.errors import (
    CanopyAIException,
    canopy_ai_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("canopyai")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    # 1. Load environment variables
    settings = get_settings()
    logger.info("Initializing %s v%s in %s environment", settings.app_name, settings.app_version, settings.environment)
    logger.info("Operational mode: %s", "MOCK (Simulated)" if settings.mock_mode else "ACTIVE SATELLITE")
    logger.info("Allowed CORS origins: %s", settings.effective_cors_origins)

    # 2. Initialize Supabase client (if credentials exist)
    try:
        from app.services.database_service import database_service

        database_service._init_supabase_client()
        db_state = "Connected" if database_service.is_connected else "In-memory mode (credentials not configured)"
        logger.info("Supabase database status: %s", db_state)
    except Exception as exc:
        logger.warning("Supabase initialization encountered error: %s. Operating with in-memory persistence.", exc)

    # 3. Initialize Earth Engine (if credentials exist)
    if not settings.mock_mode:
        try:
            from app.core.earth_engine import initialize_earth_engine

            initialize_earth_engine(
                project_id=settings.gee_project_id,
                service_account_email=settings.effective_gee_email,
                private_key_path=settings.effective_gee_key_path,
            )
            logger.info("Google Earth Engine initialized successfully")
        except Exception as exc:
            logger.warning(
                "Google Earth Engine initialization failed (%s). System will run with mock simulation fallback.",
                exc,
            )
    else:
        logger.info("MOCK_MODE=True: Google Earth Engine satellite queries operate in simulation mode.")

    # 4 & 5. Log startup status
    logger.info("CanopyAI backend startup sequence completed successfully.")
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Application factory for CanopyAI."""
    settings = get_settings()

    app = FastAPI(
        title="CanopyAI API",
        version=settings.app_version,
        description=(
            "CanopyAI estimates forest biomass and carbon "
            "storage using NASA GEDI, ESA Sentinel-2, and "
            "Google Dynamic World satellite data. Results "
            "are screening-level estimates and do not "
            "constitute formal carbon credit verification."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS for Next.js frontend (localhost:3000) and other configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.effective_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register centralized exception handlers for consistent error contracts
    app.add_exception_handler(CanopyAIException, canopy_ai_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Root welcome route
    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_prefix}/health",
            "mock_mode": settings.mock_mode,
        }

    # Mount API routers under configured prefix (default: /api)
    api_router = APIRouter(prefix=settings.api_prefix)
    api_router.include_router(health.router)
    api_router.include_router(analysis.router)
    api_router.include_router(reports.router)

    app.include_router(api_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
