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
        message: str = "Polygon area is below the minimum threshold of 10.0 hectares",
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
        message: str = "Polygon area exceeds the maximum allowable threshold of 100,000 hectares",
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


class EarthEngineUnavailableError(CanopyAIException):
    """Raised when Google Earth Engine service is unavailable."""

    def __init__(
        self,
        message: str = "Google Earth Engine service is currently unavailable",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="earth_engine_unavailable",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class EarthEngineTimeoutError(CanopyAIException):
    """Raised when a Google Earth Engine query times out."""

    def __init__(
        self,
        message: str = "Google Earth Engine query timed out",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="earth_engine_timeout",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class SatelliteQueryFailedError(CanopyAIException):
    """Raised when an Earth Engine satellite query fails to execute."""

    def __init__(
        self,
        message: str = "Satellite query failed to execute",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="satellite_query_failed",
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


class CalculationFailedError(CanopyAIException):
    """Raised when a scientific biomass or carbon calculation algorithm fails."""

    def __init__(
        self,
        message: str = "Calculation failed during biomass or carbon estimation",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="calculation_failed",
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


class AnalysisTimeoutError(CanopyAIException):
    """Raised when analysis processing exceeds the configured overall timeout."""

    def __init__(
        self,
        message: str = "Analysis exceeded 120 seconds.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="analysis_timeout",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details=details,
        )


class ReportTimeoutError(CanopyAIException):
    """Raised when PDF report generation exceeds the configured report timeout."""

    def __init__(
        self,
        message: str = "Report generation exceeded 30 seconds.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            error="report_timeout",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details=details,
        )


from app.utils.logging import get_current_request_id

# --- Centralized FastAPI Exception Handlers ---


async def canopy_ai_exception_handler(request: Request, exc: CanopyAIException) -> JSONResponse:
    """Handle custom application domain exceptions with consistent JSON formatting and request tracking."""
    req_id = get_current_request_id()
    content: Dict[str, Any] = {
        "error": exc.error,
        "message": exc.message,
    }
    if exc.details:
        content["details"] = exc.details
    if req_id:
        content["request_id"] = req_id

    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(status_code=exc.status_code, content=content, headers=headers)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic request validation errors and translate into consistent format."""
    req_id = get_current_request_id()
    # Check if the validation error is associated with the polygon field
    errors = exc.errors()
    has_polygon_error = any("polygon" in [str(loc) for loc in err.get("loc", [])] for err in errors)

    error_code = "invalid_polygon" if has_polygon_error else "invalid_request_body"
    error_messages = []
    for err in errors:
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation failed")
        error_messages.append(f"{loc}: {msg}" if loc else msg)

    content: Dict[str, Any] = {
        "error": error_code,
        "message": "; ".join(error_messages) if error_messages else "Request validation failed",
        "details": [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in errors],
    }
    if req_id:
        content["request_id"] = req_id

    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)
    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(status_code=status_code, content=content, headers=headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard Starlette / FastAPI HTTPExceptions consistently."""
    req_id = get_current_request_id()
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
        504: "gateway_timeout",
    }
    error_code = status_to_error.get(exc.status_code, "http_error")
    content: Dict[str, Any] = {
        "error": error_code,
        "message": str(exc.detail) if exc.detail else "An HTTP error occurred",
    }
    if req_id:
        content["request_id"] = req_id

    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(status_code=exc.status_code, content=content, headers=headers)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions to prevent stack trace leaks."""
    req_id = get_current_request_id()
    logger.error("Unhandled server exception on %s: %s", request.url.path, str(exc), exc_info=True)
    content: Dict[str, Any] = {
        "error": "internal_error",
        "message": "An internal server error occurred.",
    }
    if req_id:
        content["request_id"] = req_id

    headers = {"X-Request-ID": req_id} if req_id else None
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content, headers=headers)
