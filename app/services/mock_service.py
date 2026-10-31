"""Mock service providing simulated forest biomass and carbon estimation.

Allows frontend and API client development before satellite observation pipelines
(developed by Developer 1) are completed.
"""

from datetime import datetime, timezone
import math
import random
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisType,
    DataMode,
    GeoJSONPolygon,
)


def calculate_polygon_area_ha(coordinates: List[List[List[float]]]) -> float:
    """Calculate the geodesic surface area of a GeoJSON polygon in hectares using spherical excess."""
    if not coordinates or not coordinates[0] or len(coordinates[0]) < 4:
        return 0.0

    radius = 6378137.0  # WGS84 mean Earth radius in meters
    exterior_ring = coordinates[0]

    # Calculate spherical polygon area of exterior ring
    area_sq_rad = 0.0
    n = len(exterior_ring)
    for i in range(n - 1):
        p1 = exterior_ring[i]
        p2 = exterior_ring[i + 1]
        lon1 = math.radians(p1[0])
        lat1 = math.radians(p1[1])
        lon2 = math.radians(p2[0])
        lat2 = math.radians(p2[1])
        area_sq_rad += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))

    area_m2 = abs(area_sq_rad * radius * radius / 2.0)

    # Deduct interior rings (holes) if present
    for hole in coordinates[1:]:
        if len(hole) < 4:
            continue
        hole_rad = 0.0
        for i in range(len(hole) - 1):
            h1 = hole[i]
            h2 = hole[i + 1]
            hlon1 = math.radians(h1[0])
            hlat1 = math.radians(h1[1])
            hlon2 = math.radians(h2[0])
            hlat2 = math.radians(h2[1])
            hole_rad += (hlon2 - hlon1) * (2.0 + math.sin(hlat1) + math.sin(hlat2))
        area_m2 -= abs(hole_rad * radius * radius / 2.0)

    # 1 hectare = 10,000 m²
    return max(round(area_m2 / 10000.0, 8), 0.0)


class InMemoryAnalysisRepository:
    """Thread-safe in-memory repository for storing analyses during server runtime."""

    def __init__(self) -> None:
        self._storage: Dict[str, AnalysisResponse] = {}
        self._lock = threading.Lock()
        self._seed_sample_data()

    def _seed_sample_data(self) -> None:
        """Seed a representative initial analysis for immediate GET testing."""
        sample_id = "sample-amazon-basin-001"
        sample_polygon = GeoJSONPolygon(
            type="Polygon",
            coordinates=[
                [
                    [-60.05, -3.12],
                    [-60.00, -3.12],
                    [-60.00, -3.16],
                    [-60.05, -3.16],
                    [-60.05, -3.12],
                ]
            ],
        )
        area_ha = calculate_polygon_area_ha(sample_polygon.coordinates)
        sample_analysis = AnalysisResponse(
            analysis_id=sample_id,
            timestamp=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            polygon=sample_polygon,
            area_ha=area_ha,
            forest_type="Tropical Moist Broadleaf Forest",
            ecoregion="Central Amazon Moist Forests",
            canopy_cover_pct=88.5,
            canopy_data_available=True,
            mean_canopy_height_m=28.4,
            agb_t_per_ha=295.0,
            bgb_t_per_ha=70.8,
            total_biomass_t_per_ha=365.8,
            carbon_fraction=0.47,
            carbon_t_per_ha=171.93,
            co2e_t_per_ha=630.41,
            total_co2e=round(630.41 * area_ha, 2),
            confidence_score=0.91,
            confidence_label="High",
            confidence_interval_pct=8.4,
            ndvi_trend="stable",
            data_sources=["sentinel-2", "gedi", "landsat-8"],
            processing_time_seconds=1,
            data_mode=DataMode.MOCK,
            dominant_land_cover="Tree cover",
            classification_method="Simulated / Latitudinal Biome Screening",
            classification_confidence="High",
            recommended_standard="IPCC Tier 1 / Tier 2 Screening",
            data_warnings=[],
            validation_summary={"valid_geometry": True, "area_ha": round(area_ha, 4)},
            uncertainty={"empirical_interval_pct": 8.4},
            disclaimer="SIMULATED DATA (MOCK MODE): Generated for local testing. Estimates do not constitute verified carbon credits.",
        )
        self._storage[sample_id] = sample_analysis

    def save(self, analysis: AnalysisResponse) -> AnalysisResponse:
        """Store an analysis in the in-memory cache."""
        with self._lock:
            self._storage[analysis.analysis_id] = analysis
            return analysis

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisResponse]:
        """Retrieve an analysis by its unique ID."""
        with self._lock:
            return self._storage.get(analysis_id)

    def list(self, page: int = 1, limit: int = 10) -> Tuple[List[AnalysisResponse], int]:
        """Retrieve a paginated slice of stored analyses, newest first."""
        with self._lock:
            # Sort newest first by timestamp
            sorted_items = sorted(
                self._storage.values(),
                key=lambda a: a.timestamp,
                reverse=True,
            )
            total = len(sorted_items)
            start = (page - 1) * limit
            end = start + limit
            page_items = sorted_items[start:end]
            return page_items, total

    def list_offset(self, limit: int = 20, offset: int = 0) -> Tuple[List[AnalysisResponse], int]:
        """Retrieve a slice of stored analyses using limit and offset, newest first."""
        with self._lock:
            sorted_items = sorted(
                self._storage.values(),
                key=lambda a: a.timestamp,
                reverse=True,
            )
            total = len(sorted_items)
            return sorted_items[offset : offset + limit], total

    def count(self) -> int:
        """Count total stored analyses."""
        with self._lock:
            return len(self._storage)

    def clear(self) -> None:
        """Clear all stored analyses (for test isolation)."""
        with self._lock:
            self._storage.clear()


# Global singleton repository for server lifecycle
mock_repository = InMemoryAnalysisRepository()


class MockAnalysisService:
    """Simulated analysis engine implementing realistic ecological biomass and carbon estimates."""

    def __init__(self, repository: Optional[InMemoryAnalysisRepository] = None) -> None:
        self.repository = repository or mock_repository

    def generate_analysis(
        self,
        request: AnalysisRequest,
        computed_area_ha: Optional[float] = None,
        data_warnings: Optional[List[str]] = None,
    ) -> AnalysisResponse:
        """Generate a realistic, simulated carbon and biomass assessment for the provided polygon."""
        start_time = time.time()

        # Compute area in hectares if not provided
        area_ha = (
            computed_area_ha
            if computed_area_ha is not None
            else calculate_polygon_area_ha(request.polygon.coordinates)
        )

        # Determine center latitude/longitude for biome determination
        exterior = request.polygon.coordinates[0]
        avg_lon = sum(pt[0] for pt in exterior) / len(exterior)
        avg_lat = sum(pt[1] for pt in exterior) / len(exterior)

        # Derive realistic regional ecology characteristics
        if abs(avg_lat) < 23.5:
            # Tropical zone
            forest_type = "Tropical Moist Broadleaf Forest"
            ecoregion = "Tropical Forest Biome (Equatorial)"
            base_canopy_cover = 85.0 + (abs(avg_lat) % 5.0)
            base_height = 27.5 + (abs(avg_lon) % 4.0)
            agb_t_per_ha = 280.0 + ((avg_lon + avg_lat) % 35.0)
            root_shoot_ratio = 0.24
            carbon_fraction = 0.47
            ndvi_trend = "stable"
        elif abs(avg_lat) < 45.0:
            # Subtropical / Temperate zone
            forest_type = "Temperate Mixed Forest"
            ecoregion = "Temperate Broadleaf & Mixed Forest"
            base_canopy_cover = 74.0 + (abs(avg_lat) % 8.0)
            base_height = 21.0 + (abs(avg_lon) % 3.0)
            agb_t_per_ha = 165.0 + ((avg_lon + avg_lat) % 30.0)
            root_shoot_ratio = 0.22
            carbon_fraction = 0.475
            ndvi_trend = "increasing"
        else:
            # Boreal / Taiga zone
            forest_type = "Boreal Coniferous Forest"
            ecoregion = "Boreal Forests / Taiga"
            base_canopy_cover = 65.0 + (abs(avg_lat) % 10.0)
            base_height = 15.0 + (abs(avg_lon) % 3.0)
            agb_t_per_ha = 95.0 + ((avg_lon + avg_lat) % 20.0)
            root_shoot_ratio = 0.26
            carbon_fraction = 0.48
            ndvi_trend = "stable"

        # Refine values based on analysis_type (quick vs detailed)
        if request.analysis_type == AnalysisType.DETAILED:
            confidence_score = 0.91
            confidence_label = "High"
            confidence_interval_pct = 7.8
            simulated_delay = 0.05
        else:
            confidence_score = 0.82
            confidence_label = "Moderate"
            confidence_interval_pct = 14.5
            simulated_delay = 0.02

        # Small micro-pause to simulate compute without blocking
        time.sleep(simulated_delay)

        # Biomass calculations (standard IPCC Tier 1/2 formulas)
        bgb_t_per_ha = agb_t_per_ha * root_shoot_ratio
        total_biomass_t_per_ha = agb_t_per_ha + bgb_t_per_ha

        # Carbon stock (Carbon = Biomass * Carbon Fraction)
        carbon_t_per_ha = total_biomass_t_per_ha * carbon_fraction

        # CO2 equivalent (CO2e = C * 44/12 ≈ C * 3.6667)
        co2e_t_per_ha = carbon_t_per_ha * (44.0 / 12.0)
        total_co2e = co2e_t_per_ha * area_ha

        elapsed = time.time() - start_time
        processing_time = max(1, int(round(elapsed)))

        warnings_list = list(data_warnings or [])

        analysis = AnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            polygon=request.polygon,
            area_ha=round(area_ha, 4),
            forest_type=forest_type,
            ecoregion=ecoregion,
            canopy_cover_pct=round(min(base_canopy_cover, 100.0), 2),
            canopy_data_available=True,
            mean_canopy_height_m=round(base_height, 2),
            agb_t_per_ha=round(agb_t_per_ha, 2),
            bgb_t_per_ha=round(bgb_t_per_ha, 2),
            total_biomass_t_per_ha=round(total_biomass_t_per_ha, 2),
            carbon_fraction=round(carbon_fraction, 3),
            carbon_t_per_ha=round(carbon_t_per_ha, 2),
            co2e_t_per_ha=round(co2e_t_per_ha, 2),
            total_co2e=round(total_co2e, 2),
            confidence_score=confidence_score,
            confidence_label=confidence_label,
            confidence_interval_pct=confidence_interval_pct,
            ndvi_trend=ndvi_trend,
            data_sources=request.data_sources or ["sentinel-2", "gedi"],
            processing_time_seconds=processing_time,
            data_mode=DataMode.MOCK,
            dominant_land_cover="Tree cover",
            classification_method="Simulated / Latitudinal Biome Screening",
            classification_confidence="High",
            recommended_standard="IPCC Tier 1 / Tier 2 Screening",
            data_warnings=warnings_list,
            validation_summary={"valid_geometry": True, "area_ha": round(area_ha, 4)},
            uncertainty={"empirical_interval_pct": confidence_interval_pct},
            disclaimer="SIMULATED DATA (MOCK MODE): Generated for local testing. Estimates do not constitute verified carbon credits.",
        )

        # Persist in in-memory repository
        self.repository.save(analysis)
        return analysis
