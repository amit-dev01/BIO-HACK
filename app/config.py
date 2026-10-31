"""Application configuration module for CanopyAI."""

from functools import lru_cache
from typing import List, Optional, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the CanopyAI application.

    All settings can be overridden via environment variables or a .env file.
    """

    # Project metadata
    app_name: str = Field(default="CanopyAI API", description="Name of the API service")
    app_version: str = Field(default="1.0.0", description="API version")
    api_prefix: str = Field(default="/api", description="Base prefix for API endpoints")
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host binding")
    port: int = Field(default=8000, description="Server port")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://canopyai.vercel.app",
        ],
        description="Allowed CORS origins, defaults to local dev and production frontend",
    )
    frontend_url: Optional[str] = Field(
        default="https://canopyai.vercel.app",
        description="Optional single frontend deployment URL added to allowed CORS origins",
    )

    # Operational modes
    mock_mode: bool = Field(
        default=True,
        description="Run in mock mode without requiring Earth Engine or Supabase credentials",
    )

    # Polygon operational validation limits (in hectares)
    min_polygon_area_ha: float = Field(
        default=10.0,
        description="Minimum allowable polygon area in hectares (default: 10 ha)",
    )
    max_polygon_area_ha: float = Field(
        default=100000.0,
        description="Maximum allowable polygon area in hectares (default: 100,000 ha)",
    )

    # Timeout management (in seconds)
    gee_timeout_seconds: Union[int, float] = Field(
        default=60,
        description="Timeout for Google Earth Engine queries in seconds (default: 60s)",
    )
    analysis_timeout_seconds: Union[int, float] = Field(
        default=120,
        description="Overall timeout for POST /api/analyze requests in seconds (default: 120s)",
    )
    database_timeout_seconds: Union[int, float] = Field(
        default=10,
        description="Timeout for database read/write operations in seconds (default: 10s)",
    )
    pdf_timeout_seconds: Union[int, float] = Field(
        default=30,
        description="Timeout for PDF report generation in seconds (default: 30s)",
    )

    # In-memory Caching TTL (in seconds)
    analysis_cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL in seconds for individual analysis results (default: 1 hour)",
    )
    list_cache_ttl_seconds: int = Field(
        default=60,
        description="Cache TTL in seconds for paginated analysis history (default: 60s)",
    )

    # Error monitoring: Sentry
    sentry_dsn: Optional[str] = Field(
        default=None,
        description="Optional Sentry DSN for production exception and APM monitoring",
    )

    # External services: Supabase
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_service_key: Optional[str] = Field(default=None, description="Supabase service role key (backend-only)")
    supabase_key: Optional[str] = Field(default=None, description="Supabase anon or fallback key")

    # External services: Google Earth Engine
    gee_service_account_email: Optional[str] = Field(
        default=None,
        description="Google Earth Engine service account email",
    )
    gee_private_key_path: Optional[str] = Field(
        default=None,
        description="Path to Google Earth Engine private key JSON file",
    )
    gee_private_key: Optional[str] = Field(
        default=None,
        description="Raw Google Earth Engine private key JSON string",
    )
    gee_project_id: Optional[str] = Field(
        default=None,
        description="Google Cloud / Earth Engine project ID",
    )
    earth_engine_service_account: Optional[str] = Field(
        default=None,
        description="Backward-compatible alias for GEE service account email",
    )
    earth_engine_private_key: Optional[str] = Field(
        default=None,
        description="Backward-compatible alias for GEE private key path or key data",
    )

    # PDF Report generation settings
    pdf_report_title: str = Field(default="CanopyAI Forest Carbon Assessment", description="Title for PDF reports")
    pdf_primary_color: str = Field(default="#1B5E20", description="Primary brand color for PDF reports (RGB: 27, 94, 32)")
    pdf_page_size: str = Field(default="A4", description="Page size standard for reports")

    @property
    def effective_supabase_key(self) -> Optional[str]:
        """Return the active Supabase key, prioritizing the service role key."""
        return self.supabase_service_key or self.supabase_key

    @property
    def effective_gee_email(self) -> Optional[str]:
        """Return the active GEE service account email."""
        return self.gee_service_account_email or self.earth_engine_service_account

    @property
    def effective_gee_key_path(self) -> Optional[str]:
        """Return the active GEE private key path or raw key data."""
        return self.gee_private_key_path or self.gee_private_key or self.earth_engine_private_key

    @property
    def effective_cors_origins(self) -> List[str]:
        """Return all allowed CORS origins including frontend_url if set."""
        origins = list(self.cors_origins)
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        return origins

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached instance of application settings."""
    return Settings()
