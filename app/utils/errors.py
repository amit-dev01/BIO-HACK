"""Centralized error handling and exception definitions for CanopyAI."""

import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("canopyai.errors")


class CanopyAIException(Exception):
    """Base exception for all CanopyAI application domain errors."""

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class InvalidPolygonError(CanopyAIException):
    """Raised when the provided GeoJSON polygon fails geometric or syntactic validation."""

    def __init__(
        self,
        message: str = "Invalid GeoJSON polygon provided",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="invalid_polygon",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class PolygonTooSmallError(CanopyAIException):
    """Raised when the polygon area is smaller than the minimum supported threshold."""

    def __init__(
        self,
        message: str = "Polygon area is below the minimum threshold of 0.01 hectares",
        area_ha: Optional[float] = None,
        min_ha: Optional[float] = None,
    ) -> None:
        details = {}
        if area_ha is not None:
            details["area_ha"] = area_ha
        if min_ha is not None:
            details["min_ha"] = min_ha
        super().__init__(
            error="polygon_too_small",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class PolygonTooLargeError(CanopyAIException):
    """Raised when the polygon area exceeds the maximum supported threshold."""

    def __init__(
        self,
        message: str = "Polygon area exceeds the maximum allowable threshold of 200,000 hectares",
        area_ha: Optional[float] = None,
        max_ha: Optional[float] = None,
    ) -> None:
        details = {}
        if area_ha is not None:
            details["area_ha"] = area_ha
        if max_ha is not None:
            details["max_ha"] = max_ha
        super().__init__(
            error="polygon_too_large",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class AnalysisNotFoundError(CanopyAIException):
    """Raised when an analysis with the requested ID does not exist."""

    def __init__(
        self,
        analysis_id: str,
        message: Optional[str] = None,
    ) -> None:
        msg = message or f"Analysis with ID '{analysis_id}' was not found"
        super().__init__(
            error="analysis_not_found",
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"analysis_id": analysis_id},
        )


class SatelliteUnavailableError(CanopyAIException):
    """Raised when satellite observation or Earth Engine services are unreachable."""

    def __init__(
        self,
        message: str = "Satellite observation services are currently unavailable",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="satellite_unavailable",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class InternalServiceError(CanopyAIException):
    """Raised when an internal unexpected processing error occurs."""

    def __init__(
        self,
        message: str = "An unexpected error occurred during processing",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="internal_error",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class DatabaseError(CanopyAIException):
    """Raised when a persistence or database query operation fails."""

    def __init__(
        self,
        message: str = "A database error occurred while processing the request",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="database_error",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# --- Centralized FastAPI Exception Handlers ---


async def canopy_ai_exception_handler(request: Request, exc: CanopyAIException) -> JSONResponse:
    """Handle custom application domain exceptions with consistent JSON formatting."""
    content: Dict[str, Any] = {
        "error": exc.error,
        "message": exc.message,
    }
    if exc.details:
        content["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic request validation errors and translate into consistent format."""
    # Check if the validation error is associated with the polygon field
    errors = exc.errors()
    has_polygon_error = any("polygon" in [str(loc) for loc in err.get("loc", [])] for err in errors)

    error_code = "invalid_polygon" if has_polygon_error else "invalid_request"
    error_messages = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation failed")
        error_messages.append(f"{loc}: {msg}" if loc else msg)

    content = {
        "error": error_code,
        "message": "; ".join(error_messages) if error_messages else "Request validation failed",
        "details": [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in errors],
    }
    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
    return JSONResponse(status_code=status_code, content=content)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard Starlette / FastAPI HTTPExceptions consistently."""
    # Map common status codes to error identifiers
    status_to_error = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        422: "validation_error",
        500: "internal_error",
        503: "service_unavailable",
    }
    error_code = status_to_error.get(exc.status_code, "http_error")
    content = {
        "error": error_code,
        "message": str(exc.detail) if exc.detail else "An HTTP error occurred",
    }
    return JSONResponse(status_code=exc.status_code, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions to prevent stack trace leaks."""
    logger.error("Unhandled server exception encountered on %s: %s", request.url.path, str(exc), exc_info=True)
    content = {
        "error": "internal_error",
        "message": "An internal server error occurred.",
    }
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
