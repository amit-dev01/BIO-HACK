"""Tests for Phase 3 PDF Report Generation and Download Endpoint.

Covers all 10 required test scenarios:
1. PDF generation with complete analysis data
2. PDF generation with mock analysis data
3. PDF generation with missing fields
4. PDF generation with null NDVI trend
5. PDF generation with null canopy cover
6. PDF download endpoint returns correct content type (application/pdf)
7. PDF download endpoint returns correct filename
8. PDF download for non-existent analysis returns 404
9. PDF contains expected sections
10. PDF file size is reasonable (between 50KB and 500KB)
"""

from io import BytesIO
from typing import Any, Dict
from fastapi.testclient import TestClient
from PyPDF2 import PdfReader

from app.main import app
from app.services.pdf_service import generate_pdf_report

client = TestClient(app)


def get_complete_analysis_data(analysis_id: str = "complete-pdf-001") -> Dict[str, Any]:
    """Return a comprehensive analysis payload with multi-quarter NDVI trend data."""
    return {
        "analysis_id": analysis_id,
        "timestamp": "2026-02-01T14:30:00Z",
        "polygon": {
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
        },
        "area_ha": 2474.68,
        "forest_type": "Tropical Moist Broadleaf Forest",
        "ecoregion": "Central Amazon Moist Forests",
        "canopy_cover_pct": 88.5,
        "mean_canopy_height_m": 28.4,
        "agb_t_per_ha": 295.0,
        "bgb_t_per_ha": 70.8,
        "total_biomass_t_per_ha": 365.8,
        "carbon_fraction": 0.47,
        "carbon_t_per_ha": 171.93,
        "co2e_t_per_ha": 630.41,
        "total_co2e": 1560068.99,
        "annual_sequestration_tco2e": 12450.0,
        "confidence_score": 91,
        "confidence_label": "High",
        "confidence_interval_pct": 8.4,
        "data_mode": "satellite",
        "data_sources": ["Sentinel-2", "GEDI", "Landsat-8"],
        "processing_time_seconds": 0.85,
        "ndvi_trend": [
            {"quarter": "2019-Q1", "ndvi": 0.72},
            {"quarter": "2019-Q2", "ndvi": 0.74},
            {"quarter": "2019-Q3", "ndvi": 0.71},
            {"quarter": "2019-Q4", "ndvi": 0.76},
            {"quarter": "2020-Q1", "ndvi": 0.75},
            {"quarter": "2020-Q2", "ndvi": 0.78},
            {"quarter": "2020-Q3", "ndvi": 0.77},
            {"quarter": "2020-Q4", "ndvi": 0.81},
            {"quarter": "2021-Q1", "ndvi": 0.80},
            {"quarter": "2021-Q2", "ndvi": 0.83},
            {"quarter": "2021-Q3", "ndvi": 0.82},
            {"quarter": "2021-Q4", "ndvi": 0.84},
        ],
    }


# --- 1. PDF generation with complete analysis data ---


def test_pdf_generation_complete_data():
    """Verify generating PDF with complete data returns valid PDF stream."""
    data = get_complete_analysis_data("test-complete")
    pdf_bytes = generate_pdf_report(data)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")

    # Verify readable by PDF reader
    reader = PdfReader(BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1


# --- 2. PDF generation with mock analysis data ---


def test_pdf_generation_mock_data():
    """Verify PDF generated with mock mode data clearly indicates 'Mock Data'."""
    data = get_complete_analysis_data("test-mock")
    data["data_mode"] = "mock"

    pdf_bytes = generate_pdf_report(data)
    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = " ".join(page.extract_text() for page in reader.pages)

    assert "Mock Data" in full_text
    assert "simulated data" in full_text.lower()


# --- 3. PDF generation with missing fields ---


def test_pdf_generation_missing_fields():
    """Verify PDF generates without error when optional ecological fields are missing."""
    sparse_data = {
        "analysis_id": "test-sparse-001",
        "area_ha": 150.0,
        "total_co2e": None,
        "forest_type": None,
        "ecoregion": None,
        "mean_canopy_height_m": None,
        "agb_t_per_ha": None,
        "bgb_t_per_ha": None,
        "total_biomass_t_per_ha": None,
        "carbon_fraction": None,
        "carbon_t_per_ha": None,
        "co2e_t_per_ha": None,
        "confidence_score": None,
        "data_mode": "mock",
        "data_sources": [],
        "ndvi_trend": None,
    }

    pdf_bytes = generate_pdf_report(sparse_data)
    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = " ".join(page.extract_text() for page in reader.pages)
    assert "N/A" in full_text


# --- 4. PDF generation with null NDVI trend ---


def test_pdf_generation_null_ndvi_trend():
    """Verify null NDVI trend displays fallback message without failing."""
    data = get_complete_analysis_data("test-no-ndvi")
    data["ndvi_trend"] = None

    pdf_bytes = generate_pdf_report(data)
    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = " ".join(page.extract_text() for page in reader.pages)
    assert "Vegetation trend data unavailable." in full_text


# --- 5. PDF generation with null canopy cover ---


def test_pdf_generation_null_canopy_cover():
    """Verify null canopy cover displays 'N/A' in key metrics summary."""
    data = get_complete_analysis_data("test-no-canopy")
    data["canopy_cover_pct"] = None

    pdf_bytes = generate_pdf_report(data)
    assert pdf_bytes.startswith(b"%PDF")

    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = " ".join(page.extract_text() for page in reader.pages)
    assert "N/A" in full_text


# --- 6. PDF download endpoint returns correct content type ---


def test_download_endpoint_content_type():
    """Verify GET /api/reports/{id}/download returns application/pdf content type."""
    sample_id = "sample-amazon-basin-001"
    response = client.get(f"/api/reports/{sample_id}/download")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


# --- 7. PDF download endpoint returns correct filename ---


def test_download_endpoint_filename():
    """Verify Content-Disposition header contains canopyai_report_{analysis_id}.pdf."""
    sample_id = "sample-amazon-basin-001"
    response = client.get(f"/api/reports/{sample_id}/download")

    assert response.status_code == 200
    disposition = response.headers.get("content-disposition", "")
    expected_filename = f"canopyai_report_{sample_id}.pdf"
    assert expected_filename in disposition


# --- 8. PDF download for non-existent analysis returns 404 ---


def test_download_endpoint_missing_analysis_404():
    """Verify requesting a non-existent analysis ID returns HTTP 404."""
    response = client.get("/api/reports/non-existent-analysis-id-404/download")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


# --- 9. PDF contains expected sections ---


def test_pdf_contains_expected_sections():
    """Verify all 8 mandatory sections are present in the rendered document."""
    data = get_complete_analysis_data("test-sections")
    pdf_bytes = generate_pdf_report(data)

    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = " ".join(page.extract_text() for page in reader.pages)

    # Section 1: Header
    assert "CanopyAI Forest Carbon Assessment" in full_text
    assert "Pre-Screening Report" in full_text
    assert "test-sections" in full_text
    assert "Satellite Data" in full_text

    # Section 2: Key Metrics Summary
    assert "TOTAL CARBON STOCK" in full_text or "Total Carbon Stock" in full_text
    assert "FOREST AREA" in full_text or "Forest Area" in full_text
    assert "CANOPY COVER" in full_text or "Canopy Cover" in full_text
    assert "CONFIDENCE SCORE" in full_text or "Confidence Score" in full_text

    # Section 3: Forest Characteristics Table
    assert "Forest Characteristics" in full_text
    assert "Tropical Moist Broadleaf Forest" in full_text
    assert "Central Amazon Moist Forests" in full_text

    # Section 4: Carbon Stock Table
    assert "Carbon Stock Metrics" in full_text
    assert "Carbon Stock" in full_text
    assert "Total CO" in full_text

    # Section 5: Vegetation Trend
    assert "Vegetation Trend" in full_text

    # Section 6: Data Sources
    assert "Data Sources" in full_text
    assert "Sentinel-2" in full_text

    # Section 7: Methodology Note
    assert "IPCC Tier 1 guidelines" in full_text
    assert "pre-screening estimate" in full_text
    assert "Measurement, Reporting, and Verification" in full_text

    # Section 8: Footer
    assert "Generated by CanopyAI" in full_text


# --- 10. PDF file size is reasonable (between 50KB and 500KB) ---


def test_pdf_file_size_reasonable():
    """Verify complete PDF document size falls within the acceptable 50KB to 500KB boundary."""
    data = get_complete_analysis_data("test-size-check")
    pdf_bytes = generate_pdf_report(data)

    size_bytes = len(pdf_bytes)
    size_kb = size_bytes / 1024.0

    min_size = 50 * 1024   # 50 KB
    max_size = 500 * 1024  # 500 KB

    assert min_size <= size_bytes <= max_size, (
        f"PDF size {size_kb:.2f} KB ({size_bytes} bytes) outside expected range [50KB, 500KB]"
    )
