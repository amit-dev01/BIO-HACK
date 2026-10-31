"""Tests for PDF report generation and download endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_download_report_success():
    """Verify downloading a PDF report for an existing analysis returns valid PDF stream."""
    # Retrieve the seeded sample analysis
    sample_id = "sample-amazon-basin-001"
    response = client.get(f"/api/reports/{sample_id}/download")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f"canopyai-report-{sample_id}.pdf" in response.headers["content-disposition"]
    # PDF magic byte signature "%PDF"
    assert response.content.startswith(b"%PDF")


def test_download_report_not_found():
    """Verify downloading a non-existent report returns 404 with analysis_not_found error."""
    response = client.get("/api/reports/unknown-analysis-id/download")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "analysis_not_found"
    assert "message" in data
