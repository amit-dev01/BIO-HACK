"""Tests for analysis endpoints, data contracts, and in-memory retrieval."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [-60.05, -3.12],
            [-60.00, -3.12],
            [-60.00, -3.16],
            [-60.05, -3.16],
            [-60.05, -3.12],
        ]
    ],
}


def test_post_analyze_success():
    """Verify POST /api/analyze computes a complete mock carbon estimation response."""
    payload = {
        "polygon": SAMPLE_POLYGON,
        "analysis_type": "quick",
        "data_sources": ["sentinel-2", "gedi"],
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Validate mandatory contract fields
    assert "analysis_id" in data and len(data["analysis_id"]) > 0
    assert "timestamp" in data
    assert "polygon" in data
    assert data["polygon"]["type"] == "Polygon"
    assert data["area_ha"] > 0
    assert "forest_type" in data
    assert "ecoregion" in data
    assert data["canopy_cover_pct"] > 0
    assert data["mean_canopy_height_m"] > 0
    assert data["agb_t_per_ha"] > 0
    assert data["bgb_t_per_ha"] > 0
    assert data["total_biomass_t_per_ha"] > 0
    assert data["carbon_fraction"] == 0.47
    assert data["carbon_t_per_ha"] > 0
    assert data["co2e_t_per_ha"] > 0
    assert data["total_co2e"] > 0
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert data["confidence_label"] in ["High", "Moderate", "Low"]
    assert data["confidence_interval_pct"] > 0
    assert "ndvi_trend" in data
    assert data["data_sources"] == ["sentinel-2", "gedi"]
    assert data["processing_time_seconds"] >= 0
    assert data["data_mode"] == "mock"

    # Regulatory verification: ensure no carbon credit revenue claims in keys or fields
    assert not any("credit" in k.lower() for k in data.keys())
    assert "disclaimer" in data
    assert "verified carbon credits" in data["disclaimer"].lower() or "not constitute" in data["disclaimer"].lower()


def test_post_analyze_detailed_mode():
    """Verify detailed analysis yields higher confidence metrics."""
    payload = {
        "polygon": SAMPLE_POLYGON,
        "analysis_type": "detailed",
        "data_sources": ["sentinel-2", "gedi", "landsat-8"],
    }

    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["confidence_score"] >= 0.90
    assert data["confidence_label"] == "High"
    assert data["confidence_interval_pct"] < 10.0


def test_get_analysis_by_id():
    """Verify that an analysis generated in session can be retrieved by ID."""
    # First create an analysis
    payload = {
        "polygon": SAMPLE_POLYGON,
        "analysis_type": "quick",
        "data_sources": ["sentinel-2"],
    }
    create_res = client.post("/api/analyze", json=payload)
    assert create_res.status_code == 200
    created_id = create_res.json()["analysis_id"]

    # Now retrieve it
    get_res = client.get(f"/api/analyze/{created_id}")
    assert get_res.status_code == 200
    fetched_data = get_res.json()
    assert fetched_data["analysis_id"] == created_id
    assert fetched_data["area_ha"] == create_res.json()["area_ha"]


def test_get_analyses_pagination():
    """Verify GET /api/analyses returns paginated list of analyses."""
    # Ensure at least 2 analyses exist
    for _ in range(2):
        client.post(
            "/api/analyze",
            json={"polygon": SAMPLE_POLYGON, "analysis_type": "quick", "data_sources": ["sentinel-2"]},
        )

    # Fetch page 1 with limit 2
    response = client.get("/api/analyses?page=1&limit=2")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "total_pages" in data

    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2
    assert data["total"] >= 2
    assert data["total_pages"] >= 1
