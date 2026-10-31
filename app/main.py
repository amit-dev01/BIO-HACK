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
    settings = get_settings()
    logger.info("Initializing %s v%s", settings.app_name, settings.app_version)
    logger.info("Operational mode: %s", "MOCK (Simulated)" if settings.mock_mode else "ACTIVE SATELLITE")
    logger.info("Allowed CORS origins: %s", settings.cors_origins)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Application factory for CanopyAI."""
    settings = get_settings()

    app = FastAPI(
        title="CanopyAI API",
        version=settings.app_version,
        description=(
            "CanopyAI estimates forest biomass and carbon storage using satellite observations. "
            "Developer 2 API foundation providing high-performance REST endpoints, "
            "standardized GeoJSON polygon validation, mock simulation pipelines, and PDF reporting."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS for Next.js frontend (localhost:3000) and other configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
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
