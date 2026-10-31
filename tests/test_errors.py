"""Tests for validation errors, domain constraints, and error response consistency."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_polygon_not_closed():
    """Verify non-closed polygon returns consistent invalid_polygon error."""
    unclosed_polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.05, -3.12],
                [-60.00, -3.12],
                [-60.00, -3.16],
                [-60.05, -3.16],
                [-60.04, -3.11],  # Does not match first point
            ]
        ],
    }
    response = client.post(
        "/api/analyze",
        json={"polygon": unclosed_polygon, "analysis_type": "quick"},
    )
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["error"] == "invalid_polygon"
    assert "message" in data


def test_invalid_polygon_fewer_than_4_coordinates():
    """Verify polygon with fewer than 4 points fails validation."""
    triangle_unclosed = {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.05, -3.12],
                [-60.00, -3.12],
                [-60.05, -3.12],
            ]
        ],
    }
    response = client.post(
        "/api/analyze",
        json={"polygon": triangle_unclosed, "analysis_type": "quick"},
    )
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["error"] == "invalid_polygon"
    assert "message" in data


def test_invalid_polygon_out_of_bounds_coordinates():
    """Verify out-of-range latitude/longitude coordinates fail."""
    out_of_bounds = {
        "type": "Polygon",
        "coordinates": [
            [
                [-195.0, -3.12],
                [-60.0, -3.12],
                [-60.0, -3.16],
                [-195.0, -3.16],
                [-195.0, -3.12],
            ]
        ],
    }
    response = client.post(
        "/api/analyze",
        json={"polygon": out_of_bounds, "analysis_type": "quick"},
    )
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["error"] == "invalid_polygon"
    assert "message" in data


def test_polygon_too_small():
    """Verify microscopic polygon (<0.01 ha) triggers polygon_too_small error."""
    # A small 5m x 5m area (~0.0025 ha, below the 0.01 ha minimum)
    tiny_box = {
        "type": "Polygon",
        "coordinates": [
            [
                [-60.00005, -3.12005],
                [-60.00000, -3.12005],
                [-60.00000, -3.12000],
                [-60.00005, -3.12000],
                [-60.00005, -3.12005],
            ]
        ],
    }
    response = client.post(
        "/api/analyze",
        json={"polygon": tiny_box, "analysis_type": "quick"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "polygon_too_small"
    assert "message" in data


def test_polygon_too_large():
    """Verify polygon exceeding 200,000 ha triggers polygon_too_large error."""
    # A massive 5-degree by 5-degree bounding box (~30,000,000 ha)
    giant_box = {
        "type": "Polygon",
        "coordinates": [
            [
                [-65.0, -5.0],
                [-60.0, -5.0],
                [-60.0, 0.0],
                [-65.0, 0.0],
                [-65.0, -5.0],
            ]
        ],
    }
    response = client.post(
        "/api/analyze",
        json={"polygon": giant_box, "analysis_type": "quick"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "polygon_too_large"
    assert "message" in data


def test_missing_analysis_id():
    """Verify requesting a non-existent analysis ID returns 404 with analysis_not_found."""
    response = client.get("/api/analyze/non-existent-analysis-id-999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "analysis_not_found"
    assert "message" in data


def test_unknown_endpoint_404():
    """Verify requesting an undefined path returns consistent JSON error format."""
    response = client.get("/api/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "message" in data
