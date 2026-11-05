"""Tests for Gemini AI service and endpoints."""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.gemini_service import gemini_service

client = TestClient(app)

SAMPLE_TELEMETRY = {
    "analysis_id": "test_anlz_123",
    "area_ha": 1500.0,
    "total_co2e": 820000.0,
    "co2e_t_per_ha": 546.6,
    "canopy_cover_pct": 92.4,
    "mean_canopy_height_m": 26.5,
    "forest_type": "Tropical Moist Broadleaf Forest",
    "confidence_score": 92,
    "confidence_label": "High (Tier 3)",
    "recommended_standard": "Verra VCS (VM0047)",
}


def test_gemini_narrative_without_api_key():
    """Verify that without API key, service gracefully returns baseline narrative."""
    with patch.object(gemini_service, "_get_client", return_value=None):
        narrative = gemini_service.generate_ecological_narrative(SAMPLE_TELEMETRY)
        assert "executive_summary" in narrative
        assert "permanence_and_risk" in narrative
        assert "registry_compliance" in narrative
        assert "1,500.0" in narrative["executive_summary"]


def test_gemini_chat_without_api_key():
    """Verify chat endpoint returns clear guidance when API key is unconfigured."""
    with patch.object(gemini_service, "_get_client", return_value=None):
        chat_resp = gemini_service.chat_with_forest(SAMPLE_TELEMETRY, "How much carbon is stored?")
        assert "reply" in chat_resp
        assert chat_resp["configured"] is False


def test_ai_narrative_endpoint():
    """Verify POST /api/ai/narrative returns 200 with structured response."""
    res = client.post("/api/ai/narrative", json={"analysis_data": SAMPLE_TELEMETRY})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "narrative" in data
    assert "executive_summary" in data["narrative"]


def test_ai_chat_endpoint():
    """Verify POST /api/ai/chat returns 200 with reply."""
    res = client.post(
        "/api/ai/chat",
        json={
            "analysis_data": SAMPLE_TELEMETRY,
            "question": "What is the forest canopy cover?",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "reply" in data

