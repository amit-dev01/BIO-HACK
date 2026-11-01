"""FastAPI application entrypoint for CanopyAI backend API service."""

from contextlib import asynccontextmanager
import logging
import os
import time
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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
from app.utils.logging import (
    generate_request_id,
    request_id_var,
    set_current_request_id,
    setup_logging,
)

# Initialize structured logging
setup_logging()
logger = logging.getLogger("canopyai")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    # 1. Load environment variables
    settings = get_settings()

    # Configure Sentry error monitoring if DSN is set
    sentry_dsn = settings.sentry_dsn or os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration

            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FastApiIntegration()],
                traces_sample_rate=0.1,
                environment=settings.environment,
            )
            logger.info("Sentry APM and error monitoring initialized")
        except Exception as sentry_exc:
            logger.warning("Could not initialize Sentry: %s", sentry_exc)

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

    # 6.3 Response Compression via GZip middleware (payloads > 1000 bytes)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 5.2 Request ID tracking & structured request logging middleware
    @app.middleware("http")
    async def request_tracing_middleware(request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID") or generate_request_id()
        token = request_id_var.set(req_id)
        start_ts = time.time()

        # Log incoming API request (excluding noisy health checks from DEBUG/INFO if desired)
        if not request.url.path.endswith("/health"):
            logger.info(
                "Incoming request: %s %s",
                request.method,
                request.url.path,
                extra={"context": {"method": request.method, "path": request.url.path, "request_id": req_id}},
            )

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_ts) * 1000, 2)
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Response-Time-Ms"] = str(duration_ms)
            return response
        except Exception as exc:
            logger.error("Request unhandled failure on %s: %s", request.url.path, exc)
            raise
        finally:
            request_id_var.reset(token)

    # Configure CORS for Next.js frontend (localhost:3000, vercel) and other configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.effective_cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
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
