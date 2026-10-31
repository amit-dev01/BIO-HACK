"""Structured JSON logging module with request ID tracking for CanopyAI."""

from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import os
import secrets
from typing import Any, Dict, Optional

# Context variable to propagate request ID through async tasks
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def generate_request_id() -> str:
    """Generate a unique request ID in the format 'req_' + 12 random hex characters."""
    return f"req_{secrets.token_hex(6)}"


def get_current_request_id() -> Optional[str]:
    """Retrieve the current request ID from context."""
    return request_id_var.get()


def set_current_request_id(req_id: Optional[str]) -> None:
    """Set the current request ID in context."""
    request_id_var.set(req_id)


class StructuredJsonFormatter(logging.Formatter):
    """JSON log formatter adhering to production monitoring standards."""

    def format(self, record: logging.LogRecord) -> str:
        # Resolve request ID from log record attribute or async context
        req_id = getattr(record, "request_id", None) or get_current_request_id()

        # Extract structured context if supplied
        context: Optional[Dict[str, Any]] = None
        if hasattr(record, "context") and isinstance(record.context, dict):
            context = record.context
        elif hasattr(record, "extra") and isinstance(record.extra, dict):
            context = record.extra

        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "request_id": req_id,
            "component": record.name,
            "message": record.getMessage(),
        }

        if context:
            log_payload["context"] = context

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            log_payload["exception"] = record.exc_text

        return json.dumps(log_payload, default=str)


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure root and application loggers with structured JSON formatting."""
    level_str = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJsonFormatter())
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(StructuredJsonFormatter())
            handler.setLevel(level)

    # Ensure canopyai logger propagates with the configured level
    app_logger = logging.getLogger("canopyai")
    app_logger.setLevel(level)
