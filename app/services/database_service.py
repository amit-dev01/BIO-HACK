"""Database service module for persistent forest analysis storage with Supabase.

Provides repository operations against the Supabase PostgreSQL 'analyses' table,
with graceful fallback to in-memory persistence when credentials are unconfigured.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Union

from app.config import Settings, get_settings
from app.models.schemas import AnalysisResponse, AnalysisSummary
from app.services.mock_service import InMemoryAnalysisRepository, mock_repository
from app.utils.errors import DatabaseError

logger = logging.getLogger("canopyai.database")

TABLE_NAME = "analyses"


def _to_confidence_score_int(score: Optional[Union[float, int]]) -> Optional[int]:
    """Convert a confidence score to an integer between 0 and 100."""
    if score is None:
        return None
    try:
        val = float(score)
        if val <= 1.0:
            val = val * 100.0
        int_val = int(round(val))
        return max(0, min(100, int_val))
    except (ValueError, TypeError):
        return None


class DatabaseService:
    """Service layer managing persistence of forest analyses to Supabase or in-memory fallback."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        memory_repo: Optional[InMemoryAnalysisRepository] = None,
        supabase_client: Optional[Any] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.memory_repo = memory_repo or mock_repository
        self._supabase_client = supabase_client

        if self._supabase_client is None:
            self._init_supabase_client()

    def _init_supabase_client(self) -> None:
        """Safely initialize the Supabase client using configured environment variables."""
        url = self.settings.supabase_url
        key = self.settings.effective_supabase_key

        if url and key:
            try:
                from supabase import create_client

                self._supabase_client = create_client(url, key)
                logger.info("Supabase client initialized successfully (target: %s)", url)
            except Exception as e:
                logger.warning(
                    "Could not initialize Supabase client: %s. Falling back to in-memory mode.",
                    str(e),
                )
                self._supabase_client = None
        else:
            logger.info("Supabase credentials not configured. Operating in in-memory mode.")
            self._supabase_client = None

    @property
    def is_connected(self) -> bool:
        """Return True if Supabase client is actively initialized."""
        return self._supabase_client is not None

    def set_client(self, client: Optional[Any]) -> None:
        """Override the Supabase client (useful for dependency injection and testing)."""
        self._supabase_client = client

    def save_analysis(self, analysis_data: Union[AnalysisResponse, Dict[str, Any]]) -> AnalysisResponse:
        """Store one completed analysis in Supabase or the in-memory fallback.

        Preserves the complete analysis response and does not modify the analysis_id.
        """
        # Ensure analysis_data is an AnalysisResponse instance
        if isinstance(analysis_data, dict):
            analysis = AnalysisResponse.model_validate(analysis_data)
        else:
            analysis = analysis_data

        # Always maintain in-memory mirror for local session resilience
        self.memory_repo.save(analysis)

        if not self.is_connected:
            return analysis

        # Prepare database record
        try:
            full_response_dict = analysis.model_dump(mode="json")
            created_at_val = (
                analysis.timestamp.isoformat()
                if hasattr(analysis.timestamp, "isoformat")
                else str(analysis.timestamp)
            )
            polygon_val = (
                analysis.polygon.model_dump(mode="json")
                if hasattr(analysis.polygon, "model_dump")
                else analysis.polygon
            )
            data_mode_val = (
                analysis.data_mode.value
                if hasattr(analysis.data_mode, "value")
                else str(analysis.data_mode)
            )

            record = {
                "analysis_id": analysis.analysis_id,
                "created_at": created_at_val,
                "polygon_geojson": polygon_val,
                "area_ha": float(analysis.area_ha),
                "forest_type": analysis.forest_type,
                "total_co2e": float(analysis.total_co2e) if analysis.total_co2e is not None else None,
                "confidence_score": _to_confidence_score_int(analysis.confidence_score),
                "data_mode": data_mode_val,
                "full_response": full_response_dict,
                "status": "complete",
            }

            self._supabase_client.table(TABLE_NAME).insert(record).execute()
            logger.info("Successfully persisted analysis %s to Supabase", analysis.analysis_id)
            return analysis

        except Exception as e:
            logger.error("Failed to insert analysis %s into Supabase: %s", analysis.analysis_id, str(e), exc_info=True)
            raise DatabaseError(
                message=f"Database error while saving analysis: {str(e)}",
                details={"analysis_id": analysis.analysis_id},
            )

    def get_analysis_by_id(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """Retrieve the complete analysis response by ID.

        Returns None if the analysis does not exist.
        """
        if not self.is_connected:
            return self.memory_repo.get_by_id(analysis_id)

        try:
            res = (
                self._supabase_client.table(TABLE_NAME)
                .select("full_response")
                .eq("analysis_id", analysis_id)
                .execute()
            )

            if res.data and len(res.data) > 0:
                full_resp = res.data[0].get("full_response")
                if full_resp:
                    return AnalysisResponse.model_validate(full_resp)

            # Check in-memory mirror if not found in database (e.g. seeded sample)
            return self.memory_repo.get_by_id(analysis_id)

        except Exception as e:
            logger.error("Failed to query analysis %s from Supabase: %s", analysis_id, str(e), exc_info=True)
            raise DatabaseError(
                message=f"Database error while retrieving analysis: {str(e)}",
                details={"analysis_id": analysis_id},
            )

    def list_analyses(self, limit: int = 20, offset: int = 0) -> List[AnalysisSummary]:
        """Retrieve analysis summaries ordered by creation date (newest first) with pagination support."""
        # Enforce boundaries
        limit = max(1, min(100, limit))
        offset = max(0, offset)

        if not self.is_connected:
            items, _ = self.memory_repo.list_offset(limit=limit, offset=offset)
            summaries: List[AnalysisSummary] = []
            for item in items:
                summaries.append(
                    AnalysisSummary(
                        analysis_id=item.analysis_id,
                        timestamp=item.timestamp,
                        area_ha=item.area_ha,
                        total_co2e=item.total_co2e,
                        forest_type=item.forest_type,
                        confidence_score=_to_confidence_score_int(item.confidence_score),
                        status="complete",
                    )
                )
            return summaries

        try:
            res = (
                self._supabase_client.table(TABLE_NAME)
                .select("analysis_id, created_at, area_ha, total_co2e, forest_type, confidence_score, status, full_response")
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            summaries = []
            for row in res.data or []:
                # Parse timestamp
                raw_created = row.get("created_at")
                if isinstance(raw_created, str):
                    try:
                        ts = datetime.fromisoformat(raw_created.replace("Z", "+00:00"))
                    except Exception:
                        ts = datetime.now(timezone.utc)
                elif isinstance(raw_created, datetime):
                    ts = raw_created
                else:
                    ts = datetime.now(timezone.utc)

                summaries.append(
                    AnalysisSummary(
                        analysis_id=row["analysis_id"],
                        timestamp=ts,
                        area_ha=float(row.get("area_ha", 0.0)),
                        total_co2e=float(row["total_co2e"]) if row.get("total_co2e") is not None else None,
                        forest_type=row.get("forest_type"),
                        confidence_score=_to_confidence_score_int(row.get("confidence_score")),
                        status=row.get("status", "complete"),
                    )
                )
            return summaries

        except Exception as e:
            logger.error("Failed to list analyses from Supabase: %s", str(e), exc_info=True)
            raise DatabaseError(message=f"Database error while listing analyses: {str(e)}")

    def count_analyses(self) -> int:
        """Return the total number of saved analyses."""
        if not self.is_connected:
            return self.memory_repo.count()

        try:
            res = (
                self._supabase_client.table(TABLE_NAME)
                .select("analysis_id", count="exact")
                .limit(1)
                .execute()
            )
            if res.count is not None:
                return res.count
            return len(res.data or [])

        except Exception as e:
            logger.error("Failed to count analyses in Supabase: %s", str(e), exc_info=True)
            raise DatabaseError(message=f"Database error while counting analyses: {str(e)}")


# Singleton service instance
database_service = DatabaseService()


# --- Public Functional Interface (Section 6) ---


def save_analysis(analysis_data: Union[AnalysisResponse, Dict[str, Any]]) -> AnalysisResponse:
    """Store one completed analysis. Public function interface."""
    return database_service.save_analysis(analysis_data)


def get_analysis_by_id(analysis_id: str) -> Optional[AnalysisResponse]:
    """Retrieve the complete stored response. Public function interface."""
    return database_service.get_analysis_by_id(analysis_id)


def list_analyses(limit: int = 20, offset: int = 0) -> List[AnalysisSummary]:
    """Return analyses ordered by creation date, newest first. Public function interface."""
    return database_service.list_analyses(limit=limit, offset=offset)


def count_analyses() -> int:
    """Return the total number of saved analyses. Public function interface."""
    return database_service.count_analyses()
