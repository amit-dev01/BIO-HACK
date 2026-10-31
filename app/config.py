"""Application configuration module for CanopyAI."""

from functools import lru_cache
from typing import List, Optional
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

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host binding")
    port: int = Field(default=8000, description="Server port")

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins, defaults to Next.js development server",
    )

    # Operational modes
    mock_mode: bool = Field(
        default=True,
        description="Run in mock mode without requiring Earth Engine or Supabase credentials",
    )

    # Polygon validation limits (in hectares)
    min_polygon_area_ha: float = Field(
        default=0.01,
        description="Minimum allowable polygon area in hectares (default: 0.01 ha / 100 m²)",
    )
    max_polygon_area_ha: float = Field(
        default=200000.0,
        description="Maximum allowable polygon area in hectares (default: 200,000 ha)",
    )

    # External services (optional for mock mode, required for persistent Supabase storage)
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_service_key: Optional[str] = Field(default=None, description="Supabase service role key (backend-only)")
    supabase_key: Optional[str] = Field(default=None, description="Supabase anon or fallback key")
    earth_engine_service_account: Optional[str] = Field(default=None, description="Google Earth Engine service account")
    earth_engine_private_key: Optional[str] = Field(default=None, description="Google Earth Engine private key")

    # PDF Report generation settings
    pdf_report_title: str = Field(default="CanopyAI Forest Carbon Assessment", description="Title for PDF reports")
    pdf_primary_color: str = Field(default="#1B5E20", description="Primary brand color for PDF reports (RGB: 27, 94, 32)")
    pdf_page_size: str = Field(default="A4", description="Page size standard for reports")

    @property
    def effective_supabase_key(self) -> Optional[str]:
        """Return the active Supabase key, prioritizing the service role key."""
        return self.supabase_service_key or self.supabase_key

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
