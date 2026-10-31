"""Seed database with 10 impressive global forest carbon analyses for demo presentation.

Loads demo polygons from demo/demo_polygons.json if available, or uses curated
canonical forest biomes globally (Amazon, Congo, Pacific Northwest, Taiga, etc.).
"""

from datetime import datetime, timezone
import json
import logging
import os
import sys
import uuid

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.schemas import AnalysisResponse, DataMode, GeoJSONPolygon
from app.services.database_service import database_service
from app.services.mock_service import MockAnalysisService, mock_repository

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("canopyai.seed")

# 10 Curated Global Forest Biomes for Demo
CURATED_DEMO_SITES = [
    {
        "name": "Amazon Basin Rainforest — Tapajós National Forest, Brazil",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "Tapajós-Xingu Moist Forests",
        "coordinates": [
            [
                [-55.10, -3.10],
                [-55.00, -3.10],
                [-55.00, -3.20],
                [-55.10, -3.20],
                [-55.10, -3.10],
            ]
        ],
        "agb": 312.4,
        "height": 29.8,
        "cover": 94.2,
        "ndvi": 0.88,
    },
    {
        "name": "Congo Basin Peatland Forest — Salonga National Park, DRC",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "Central Congolian Lowland Forests",
        "coordinates": [
            [
                [20.50, -2.10],
                [20.60, -2.10],
                [20.60, -2.20],
                [20.50, -2.20],
                [20.50, -2.10],
            ]
        ],
        "agb": 288.7,
        "height": 27.5,
        "cover": 91.0,
        "ndvi": 0.85,
    },
    {
        "name": "Pacific Northwest Temperate Rainforest — Olympic Peninsula, USA",
        "forest_type": "Temperate Mixed Forest",
        "ecoregion": "Central Pacific Coastal Forests",
        "coordinates": [
            [
                [-124.10, 47.70],
                [-124.00, 47.70],
                [-124.00, 47.60],
                [-124.10, 47.60],
                [-124.10, 47.70],
            ]
        ],
        "agb": 385.2,
        "height": 38.6,
        "cover": 89.5,
        "ndvi": 0.84,
    },
    {
        "name": "Boreal Coniferous Forest — Lake Baikal Taiga, Russia",
        "forest_type": "Boreal Coniferous Forest",
        "ecoregion": "East Siberian Taiga",
        "coordinates": [
            [
                [108.50, 53.50],
                [108.60, 53.50],
                [108.60, 53.40],
                [108.50, 53.40],
                [108.50, 53.50],
            ]
        ],
        "agb": 115.0,
        "height": 16.2,
        "cover": 72.0,
        "ndvi": 0.68,
    },
    {
        "name": "Sundaland Dipterocarp Forest — Borneo Heart of Borneo, Malaysia",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "Borneo Lowland Rain Forests",
        "coordinates": [
            [
                [115.20, 3.80],
                [115.30, 3.80],
                [115.30, 3.70],
                [115.20, 3.70],
                [115.20, 3.80],
            ]
        ],
        "agb": 340.5,
        "height": 33.2,
        "cover": 95.8,
        "ndvi": 0.89,
    },
    {
        "name": "Valdivian Temperate Rainforest — Los Ríos Region, Chile",
        "forest_type": "Temperate Mixed Forest",
        "ecoregion": "Valdivian Temperate Forests",
        "coordinates": [
            [
                [-73.40, -40.10],
                [-73.30, -40.10],
                [-73.30, -40.20],
                [-73.40, -40.20],
                [-73.40, -40.10],
            ]
        ],
        "agb": 260.4,
        "height": 24.1,
        "cover": 84.0,
        "ndvi": 0.81,
    },
    {
        "name": "Western Ghats Evergreen Forest — Silent Valley, India",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "South Western Ghats Moist Deciduous Forests",
        "coordinates": [
            [
                [76.40, 11.10],
                [76.50, 11.10],
                [76.50, 11.00],
                [76.40, 11.00],
                [76.40, 11.10],
            ]
        ],
        "agb": 275.0,
        "height": 26.5,
        "cover": 90.5,
        "ndvi": 0.86,
    },
    {
        "name": "Black Forest Montane Conifers — Baden-Württemberg, Germany",
        "forest_type": "Temperate Mixed Forest",
        "ecoregion": "Western European Broadleaf Forests",
        "coordinates": [
            [
                [8.20, 48.30],
                [8.30, 48.30],
                [8.30, 48.20],
                [8.20, 48.20],
                [8.20, 48.30],
            ]
        ],
        "agb": 195.8,
        "height": 22.0,
        "cover": 82.5,
        "ndvi": 0.79,
    },
    {
        "name": "Daintree Wet Tropics — Queensland, Australia",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "Queensland Tropical Rain Forests",
        "coordinates": [
            [
                [145.35, -16.20],
                [145.45, -16.20],
                [145.45, -16.30],
                [145.35, -16.30],
                [145.35, -16.20],
            ]
        ],
        "agb": 298.0,
        "height": 28.1,
        "cover": 92.4,
        "ndvi": 0.87,
    },
    {
        "name": "Mount Kenya Montane Forest — Central Highlands, Kenya",
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "East African Montane Forests",
        "coordinates": [
            [
                [37.25, -0.20],
                [37.35, -0.20],
                [37.35, -0.30],
                [37.25, -0.30],
                [37.25, -0.20],
            ]
        ],
        "agb": 235.6,
        "height": 23.4,
        "cover": 86.0,
        "ndvi": 0.80,
    },
]


def load_demo_polygons():
    """Load polygons from demo/demo_polygons.json if present, or return curated sites."""
    demo_file = os.path.join(os.path.dirname(__file__), "..", "demo", "demo_polygons.json")
    if os.path.exists(demo_file):
        try:
            with open(demo_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) >= 10:
                    logger.info("Loaded %d demo polygons from %s", len(data), demo_file)
                    return data
        except Exception as e:
            logger.warning("Could not read demo/demo_polygons.json: %s. Using curated sites.", e)
    return CURATED_DEMO_SITES


def seed_database() -> int:
    """Generate and persist 10 complete forest analyses into Supabase and in-memory cache."""
    sites = load_demo_polygons()
    seeded_count = 0

    from app.utils.geo import calculate_area_ha

    for idx, site in enumerate(sites[:10], start=1):
        coords = site["coordinates"]
        polygon = GeoJSONPolygon(type="Polygon", coordinates=coords)
        try:
            area_ha = round(calculate_area_ha(polygon.model_dump(mode="json")), 2)
        except Exception:
            area_ha = 1250.0

        agb = float(site.get("agb", 250.0))
        # Root-to-shoot ratio
        bgb = round(agb * 0.22, 2)
        total_biomass = round(agb + bgb, 2)
        carbon_stock = round(total_biomass * 0.47, 2)
        co2e_per_ha = round(carbon_stock * (44.0 / 12.0), 2)
        total_co2 = round(co2e_per_ha * area_ha, 2)

        analysis = AnalysisResponse(
            analysis_id=f"demo-analysis-{idx:03d}-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            polygon=polygon,
            area_ha=area_ha,
            forest_type=site.get("forest_type", "Tropical Moist Broadleaf Forest"),
            ecoregion=site.get("ecoregion", "Global Forest Biome"),
            canopy_cover_pct=float(site.get("cover", 90.0)),
            canopy_data_available=True,
            mean_canopy_height_m=float(site.get("height", 25.0)),
            agb_t_per_ha=agb,
            bgb_t_per_ha=bgb,
            total_biomass_t_per_ha=total_biomass,
            carbon_fraction=0.47,
            carbon_t_per_ha=carbon_stock,
            co2e_t_per_ha=co2e_per_ha,
            total_co2e=total_co2,
            confidence_score=0.92,
            confidence_label="High",
            confidence_interval_pct=7.5,
            ndvi_trend="stable",
            data_sources=["NASA GEDI Level 4A", "ESA Sentinel-2 Harmonized", "Google Dynamic World"],
            processing_time_seconds=1,
            data_mode=DataMode.MOCK,
            dominant_land_cover="Tree cover",
            classification_method="Earth Engine Land Cover / Geographic Biome",
            classification_confidence="High",
            recommended_standard="IPCC Guidelines for National Greenhouse Gas Inventories (Tier 1/2)",
            data_warnings=[],
            validation_summary={"valid_geometry": True, "area_ha": area_ha},
            uncertainty={"empirical_interval_pct": 7.5, "agb_stddev": 12.0},
            disclaimer="Scientific ecological estimation for monitoring purposes. Does not constitute verified or certified carbon credits.",
        )

        database_service.save_analysis(analysis)
        seeded_count += 1
        logger.info(
            "Seeded [%d/10] %s (Area: %.2f ha, Total CO2e: %.2f t)",
            idx,
            site.get("name", f"Site {idx}"),
            area_ha,
            total_co2,
        )

    logger.info("Successfully seeded %d demo analyses into repository.", seeded_count)
    return seeded_count


if __name__ == "__main__":
    seed_database()
