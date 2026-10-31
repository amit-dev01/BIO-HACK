"""Analysis service orchestrating forest carbon and biomass workflows.

Connects the API boundary to Developer 1's scientific satellite observation and carbon
calculation modules (app.core.* and app.utils.geo) while supporting mock mode and graceful fallbacks.
"""

import concurrent.futures
from datetime import datetime, timezone
import logging
import math
import time
from typing import Any, Dict, List, Optional
import uuid

from app.config import Settings, get_settings
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    DataMode,
    GeoJSONPolygon,
    PaginatedAnalysisResponse,
)
from app.services.database_service import DatabaseService, database_service
from app.services.mock_service import (
    MockAnalysisService,
    mock_repository,
)
from app.utils.errors import (
    AnalysisNotFoundError,
    InvalidPolygonError,
    PolygonTooLargeError,
    PolygonTooSmallError,
)

logger = logging.getLogger("canopyai.analysis_service")


class AnalysisService:
    """Service orchestrating the complete carbon assessment workflow.

    Workflow phases:
    1. Receive polygon
    2. Validate request structure (Pydantic)
    3. Validate polygon geometry (geo.validate_polygon)
    4. Calculate area and evaluate size bounds (geo.calculate_area_ha)
    5. Retrieve satellite observations (earth_engine.get_satellite_observations)
    6. Calculate below-ground biomass (biomass.calculate_below_ground_biomass)
    7. Calculate total biomass (biomass.calculate_total_biomass)
    8. Calculate carbon stock (carbon.calculate_carbon_stock)
    9. Calculate CO2 equivalent (carbon.calculate_co2_equivalent)
    10. Calculate total CO2 (carbon.calculate_total_co2)
    11. Evaluate data quality & confidence (confidence.calculate_confidence)
    12. Assemble analysis response
    13. Save analysis to persistence repository (with timeout & failure tolerance)
    14. Return response
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        mock_service: Optional[MockAnalysisService] = None,
        db_service: Optional[DatabaseService] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.mock_service = mock_service or MockAnalysisService(repository=mock_repository)
        self.database_service = db_service or database_service

    def validate_polygon_geometry(self, polygon: GeoJSONPolygon) -> None:
        """Validate geometric properties of the GeoJSON polygon using Developer 1's geo module."""
        if polygon.type != "Polygon":
            raise InvalidPolygonError(message=f"Expected geometry type 'Polygon', received '{polygon.type}'")

        if not polygon.coordinates or len(polygon.coordinates) == 0:
            raise InvalidPolygonError(message="Polygon must contain at least one linear ring")

        # Validate with Developer 1's geo.py validator
        from app.utils.geo import validate_polygon

        poly_dict = polygon.model_dump(mode="json")
        if not validate_polygon(poly_dict):
            raise InvalidPolygonError(message="Invalid GeoJSON polygon geometry or boundary coordinates")

    def calculate_and_validate_area(self, polygon: GeoJSONPolygon) -> float:
        """Calculate the geodesic area in hectares and enforce boundary limits."""
        from app.utils.geo import calculate_area_ha

        poly_dict = polygon.model_dump(mode="json")
        try:
            area_ha = calculate_area_ha(poly_dict)
        except Exception as exc:
            raise InvalidPolygonError(message=f"Could not calculate polygon area: {exc}") from exc

        if area_ha <= 1e-12 or math.isnan(area_ha):
            raise InvalidPolygonError(message="Computed polygon area is zero or degenerate")

        if area_ha < self.settings.min_polygon_area_ha:
            raise PolygonTooSmallError(
                message=(
                    f"Polygon area of {area_ha:.4f} ha is below the minimum threshold "
                    f"of {self.settings.min_polygon_area_ha} hectares"
                ),
                area_ha=area_ha,
                min_ha=self.settings.min_polygon_area_ha,
            )

        if area_ha > self.settings.max_polygon_area_ha:
            raise PolygonTooLargeError(
                message=(
                    f"Polygon area of {area_ha:.2f} ha exceeds the maximum allowable threshold "
                    f"of {self.settings.max_polygon_area_ha} hectares"
                ),
                area_ha=area_ha,
                max_ha=self.settings.max_polygon_area_ha,
            )

        return area_ha

    def run_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        """Execute the analysis workflow for the provided forest boundary.

        Calls Developer 1's scientific calculation modules in exact sequence:
        1. geo.validate_polygon
        2. geo.calculate_area_ha
        3. earth_engine.get_satellite_observations
        4. biomass.calculate_below_ground_biomass
        5. biomass.calculate_total_biomass
        6. carbon.calculate_carbon_stock
        7. carbon.calculate_co2_equivalent
        8. carbon.calculate_total_co2
        9. confidence.calculate_confidence
        """
        start_time = time.time()

        # 1. Validate polygon geometry
        self.validate_polygon_geometry(request.polygon)

        # 2. Calculate area and evaluate size bounds
        area_ha = self.calculate_and_validate_area(request.polygon)
        poly_dict = request.polygon.model_dump(mode="json")

        # 3. Mode selection & Earth Engine availability check
        is_mock = self.settings.mock_mode
        fallback_warning = None

        if not is_mock:
            try:
                from app.core.earth_engine import _ensure_initialized
                _ensure_initialized()
            except Exception as ee_err:
                logger.warning(
                    "Earth Engine credentials missing or initialization failed: %s. Falling back to mock mode.",
                    ee_err,
                )
                is_mock = True
                fallback_warning = "Satellite service unavailable. Results are simulated."

        if is_mock:
            warnings_list = [fallback_warning] if fallback_warning else []
            analysis = self.mock_service.generate_analysis(
                request,
                computed_area_ha=area_ha,
                data_warnings=warnings_list,
            )
            return self._save_with_timeout(analysis)

        # 4. Active Real Satellite Processing Pipeline
        data_warnings: List[str] = []
        from app.core import biomass, carbon, confidence, earth_engine
        from app.core.forest_classifier import classify_forest_type

        # 4.1 Query satellite observations with 60-second timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(earth_engine.get_satellite_observations, poly_dict)
            try:
                sat_obs = future.result(timeout=self.settings.gee_timeout_seconds)
            except concurrent.futures.TimeoutError:
                logger.warning("Earth Engine query timed out after %s seconds", self.settings.gee_timeout_seconds)
                data_warnings.append("Earth Engine query timed out after 60 seconds. Satellite observations unavailable.")
                sat_obs = {
                    "agb_t_per_ha": None,
                    "agb_stddev": None,
                    "gedi_observation_count": 0,
                    "gedi_data_available": False,
                    "mean_canopy_height_m": None,
                    "height_observation_count": 0,
                    "height_data_available": False,
                    "mean_ndvi": None,
                    "valid_pixel_percentage": None,
                    "image_count": 0,
                    "ndvi_trend": [],
                    "data_sources": ["NASA GEDI Level 4A", "ESA Sentinel-2"],
                }
            except Exception as exc:
                logger.warning("Earth Engine query failed: %s", exc)
                data_warnings.append(f"Satellite observation retrieval failed: {exc}")
                sat_obs = {
                    "agb_t_per_ha": None,
                    "agb_stddev": None,
                    "gedi_observation_count": 0,
                    "gedi_data_available": False,
                    "mean_canopy_height_m": None,
                    "height_observation_count": 0,
                    "height_data_available": False,
                    "mean_ndvi": None,
                    "valid_pixel_percentage": None,
                    "image_count": 0,
                    "ndvi_trend": [],
                    "data_sources": ["NASA GEDI Level 4A", "ESA Sentinel-2"],
                }

        # 4.2 Classify forest biome & land cover attributes
        forest_type = sat_obs.get("forest_type")
        ecoregion = sat_obs.get("ecoregion")
        dominant_land_cover = sat_obs.get("dominant_land_cover")
        classification_method = sat_obs.get("classification_method")
        classification_confidence = sat_obs.get("classification_confidence")
        recommended_standard = sat_obs.get("recommended_standard")

        if not forest_type:
            try:
                cls_res = classify_forest_type(poly_dict)
                if isinstance(cls_res, dict):
                    forest_type = cls_res.get("forest_type", "Other")
                    ecoregion = ecoregion or cls_res.get("ecoregion")
                    dominant_land_cover = dominant_land_cover or cls_res.get("dominant_land_cover")
                    classification_method = classification_method or cls_res.get("classification_method")
                    classification_confidence = classification_confidence or cls_res.get("classification_confidence")
                    recommended_standard = recommended_standard or cls_res.get("recommended_standard")
                else:
                    forest_type = str(cls_res)
            except Exception as cls_exc:
                logger.warning("Forest classification failed, using 'Other': %s", cls_exc)
                forest_type = "Other"

        if not ecoregion:
            ecoregion_map = {
                "Tropical Moist Broadleaf": "Tropical Forest Biome (Equatorial)",
                "Temperate Broadleaf": "Temperate Broadleaf & Mixed Forest",
                "Boreal Coniferous": "Boreal Forests / Taiga",
                "Other": "Non-Forest / Shrubland Biome",
            }
            ecoregion = ecoregion_map.get(forest_type, f"{forest_type} Biome")

        agb = sat_obs.get("agb_t_per_ha")

        if agb is None:
            # When satellite data returns null for biomass:
            # Set all downstream carbon fields to null.
            # Do not attempt to calculate carbon from null biomass.
            # Set confidence_score to 0.
            # Set data_mode to "satellite".
            data_warnings.append("No valid GEDI biomass observations found in the selected area.")
            bgb = None
            total_biomass = None
            carbon_stock = None
            co2e = None
            total_co2 = None
            conf_score = 0.0
            conf_label = "Low"
            conf_interval = None
        else:
            # 4.3 Calculate Below-Ground Biomass
            bgb = round(biomass.calculate_below_ground_biomass(agb, forest_type), 2)

            # 4.4 Calculate Total Biomass
            total_biomass = round(biomass.calculate_total_biomass(agb, bgb), 2)

            # 4.5 Calculate Carbon Stock
            carbon_stock = round(carbon.calculate_carbon_stock(total_biomass), 2)

            # 4.6 Calculate CO2 Equivalent
            co2e = round(carbon.calculate_co2_equivalent(carbon_stock), 2)

            # 4.7 Calculate Total CO2
            total_co2 = round(carbon.calculate_total_co2(co2e, area_ha), 2)

            # 4.8 Calculate Confidence Score
            cloud_cover_val = None
            if sat_obs.get("valid_pixel_percentage") is not None:
                cloud_cover_val = max(0.0, min(100.0, 100.0 - sat_obs["valid_pixel_percentage"]))

            conf_res = confidence.calculate_confidence(
                gedi_shot_count=sat_obs.get("gedi_observation_count"),
                biomass_uncertainty_se=sat_obs.get("agb_stddev"),
                agb_t_per_ha=agb,
                cloud_cover_pct=cloud_cover_val,
            )
            conf_score = round(conf_res["confidence_score"] / 100.0, 2)
            conf_label = conf_res["confidence_label"]
            conf_interval = conf_res.get("confidence_interval_pct")

        elapsed = time.time() - start_time
        proc_time = max(1, int(round(elapsed)))

        canopy_cov = (
            sat_obs.get("canopy_cover_pct")
            if sat_obs.get("canopy_cover_pct") is not None
            else sat_obs.get("valid_pixel_percentage")
        )
        canopy_avail = sat_obs.get("canopy_data_available", sat_obs.get("height_data_available", False))

        if not dominant_land_cover:
            dominant_land_cover = (
                "Tree cover"
                if (agb is not None and agb > 0)
                else ("Non-Forest" if forest_type in ("Other", "Non-Forest") else "Tree cover")
            )

        classification_method = classification_method or "Earth Engine Land Cover / Geographic Biome"
        classification_confidence = (
            classification_confidence
            or ("High" if conf_score >= 0.75 else ("Medium" if conf_score >= 0.5 else "Low"))
        )
        recommended_standard = (
            recommended_standard
            or "IPCC Guidelines for National Greenhouse Gas Inventories (Tier 1/2)"
        )

        analysis = AnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            polygon=request.polygon,
            area_ha=round(area_ha, 4),
            forest_type=forest_type,
            ecoregion=ecoregion,
            canopy_cover_pct=canopy_cov,
            canopy_data_available=canopy_avail,
            mean_canopy_height_m=sat_obs.get("mean_canopy_height_m"),
            agb_t_per_ha=round(agb, 2) if agb is not None else None,
            bgb_t_per_ha=bgb,
            total_biomass_t_per_ha=total_biomass,
            carbon_fraction=0.47,
            carbon_t_per_ha=carbon_stock,
            co2e_t_per_ha=co2e,
            total_co2e=total_co2,
            confidence_score=conf_score,
            confidence_label=conf_label,
            confidence_interval_pct=conf_interval,
            ndvi_trend=sat_obs.get("ndvi_trend"),
            data_sources=sat_obs.get("data_sources") or ["NASA GEDI Level 4A", "ESA Sentinel-2"],
            processing_time_seconds=proc_time,
            data_mode=DataMode.SATELLITE,
            dominant_land_cover=dominant_land_cover,
            classification_method=classification_method,
            classification_confidence=classification_confidence,
            recommended_standard=recommended_standard,
            data_warnings=data_warnings,
            validation_summary={"valid_geometry": True, "area_ha": round(area_ha, 4)},
            uncertainty={"empirical_interval_pct": conf_interval, "agb_stddev": sat_obs.get("agb_stddev")},
            disclaimer="Scientific ecological estimation for monitoring purposes. Does not constitute verified or certified carbon credits.",
        )

        return self._save_with_timeout(analysis)

    def _save_with_timeout(self, analysis: AnalysisResponse) -> AnalysisResponse:
        """Save analysis to Supabase/memory repository with 10s timeout, non-blocking on failure."""
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.database_service.save_analysis, analysis)
                saved = future.result(timeout=self.settings.database_timeout_seconds)
                return saved
        except Exception as exc:
            logger.error(
                "Database persistence timed out or failed for analysis %s: %s",
                analysis.analysis_id,
                exc,
            )
            # The analysis result is lost in database but the user still gets their answer
            return analysis

    def get_analysis_by_id(self, analysis_id: str) -> AnalysisResponse:
        """Retrieve a previously generated analysis by its unique ID."""
        analysis = self.database_service.get_analysis_by_id(analysis_id)
        if not analysis:
            raise AnalysisNotFoundError(analysis_id=analysis_id)
        return analysis

    def list_analyses(
        self,
        limit: int = 20,
        offset: int = 0,
        page: Optional[int] = None,
    ) -> PaginatedAnalysisResponse:
        """Retrieve paginated analyses recorded in the system."""
        limit = max(1, min(100, limit))

        if page is not None and offset == 0:
            actual_offset = max(0, (page - 1) * limit)
        else:
            actual_offset = max(0, offset)

        summaries = self.database_service.list_analyses(limit=limit, offset=actual_offset)
        total = self.database_service.count_analyses()

        computed_page = (actual_offset // limit) + 1
        total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

        return PaginatedAnalysisResponse(
            total=total,
            limit=limit,
            offset=actual_offset,
            analyses=summaries,
            items=summaries,
            page=computed_page,
            total_pages=total_pages,
        )


# Global service instance
analysis_service = AnalysisService()
