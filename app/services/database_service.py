"""Database service abstraction layer.

Prepares the interface for Supabase integration in subsequent development phases.
Currently delegates to in-memory persistence or provides no-op fallbacks when
credentials are unconfigured.
"""

import logging
from typing import Optional
from app.config import Settings, get_settings
from app.models.schemas import AnalysisResponse
from app.services.mock_service import InMemoryAnalysisRepository, mock_repository

logger = logging.getLogger("canopyai.database")


class DatabaseService:
    """Persistence abstraction supporting Supabase backend with in-memory fallback."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        memory_repo: Optional[InMemoryAnalysisRepository] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.memory_repo = memory_repo or mock_repository
        self._supabase_client = None

        if self.settings.supabase_url and self.settings.supabase_key:
            try:
                from supabase import create_client

                self._supabase_client = create_client(
                    self.settings.supabase_url,
                    self.settings.supabase_key,
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.warning("Could not initialize Supabase client: %s. Using in-memory store.", e)
        else:
            logger.info("Supabase credentials not set. Operating in in-memory mode.")

    @property
    def is_connected(self) -> bool:
        """Return True if Supabase is connected."""
        return self._supabase_client is not None

    async def save_analysis(self, analysis: AnalysisResponse) -> AnalysisResponse:
        """Persist analysis result to database or in-memory fallback."""
        if self._supabase_client:
            # Future Phase: persist to Supabase analyses table
            pass
        return self.memory_repo.save(analysis)

    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """Fetch analysis by ID from database or in-memory fallback."""
        if self._supabase_client:
            # Future Phase: fetch from Supabase
            pass
        return self.memory_repo.get_by_id(analysis_id)


# Global service instance
database_service = DatabaseService()
