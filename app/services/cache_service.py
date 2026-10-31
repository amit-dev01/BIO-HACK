"""In-memory caching service for high-performance demo responses."""

import logging
import threading
import time
from typing import Any, Dict, Optional, Tuple

from app.models.schemas import AnalysisResponse, PaginatedAnalysisResponse

logger = logging.getLogger("canopyai.cache")


class InMemoryCacheService:
    """Thread-safe in-memory cache supporting TTL expiration and selective invalidation."""

    def __init__(self) -> None:
        self._analysis_cache: Dict[str, Tuple[AnalysisResponse, float]] = {}
        self._list_cache: Dict[str, Tuple[PaginatedAnalysisResponse, float]] = {}
        self._lock = threading.Lock()

    def get_analysis(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """Retrieve a cached analysis result if not expired."""
        with self._lock:
            key = f"analysis_{analysis_id}"
            entry = self._analysis_cache.get(key)
            if not entry:
                return None
            result, expiry = entry
            if time.time() > expiry:
                del self._analysis_cache[key]
                return None
            return result

    def set_analysis(
        self,
        analysis_id: str,
        result: AnalysisResponse,
        ttl_seconds: int = 3600,
    ) -> None:
        """Store an analysis result in cache with TTL (default: 1 hour)."""
        with self._lock:
            key = f"analysis_{analysis_id}"
            self._analysis_cache[key] = (result, time.time() + ttl_seconds)

    def get_list(self, limit: int, offset: int) -> Optional[PaginatedAnalysisResponse]:
        """Retrieve a cached paginated list if not expired."""
        with self._lock:
            key = f"list_{limit}_{offset}"
            entry = self._list_cache.get(key)
            if not entry:
                return None
            result, expiry = entry
            if time.time() > expiry:
                del self._list_cache[key]
                return None
            return result

    def set_list(
        self,
        limit: int,
        offset: int,
        result: PaginatedAnalysisResponse,
        ttl_seconds: int = 60,
    ) -> None:
        """Store a paginated analysis list in cache with TTL (default: 60 seconds)."""
        with self._lock:
            key = f"list_{limit}_{offset}"
            self._list_cache[key] = (result, time.time() + ttl_seconds)

    def invalidate_list_cache(self) -> None:
        """Invalidate all cached analysis list entries when a new analysis is saved."""
        with self._lock:
            self._list_cache.clear()
            logger.debug("Analysis list cache invalidated")

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._analysis_cache.clear()
            self._list_cache.clear()


# Global cache service instance
cache_service = InMemoryCacheService()

