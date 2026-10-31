"""Tests for Supabase persistence, database service, mock fallbacks, and error handling.

Covers all 10 required Phase 2 scenarios:
1. Saving an analysis
2. Retrieving an existing analysis
3. Retrieving a missing analysis
4. Listing analyses
5. Pagination
6. Empty database
7. Database unavailable
8. Mock mode without Supabase
9. Mock mode with Supabase
10. Preservation of complete response data
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisType,
    DataMode,
    GeoJSONPolygon,
)
from app.services.database_service import DatabaseService, TABLE_NAME
from app.services.mock_service import InMemoryAnalysisRepository
from app.utils.errors import DatabaseError

client = TestClient(app)

SAMPLE_POLYGON = GeoJSONPolygon(
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


def create_sample_analysis(analysis_id: str = "test-analysis-123") -> AnalysisResponse:
    """Helper to generate a fully populated AnalysisResponse."""
    return AnalysisResponse(
        analysis_id=analysis_id,
        timestamp=datetime(2026, 2, 1, 10, 30, 0, tzinfo=timezone.utc),
        polygon=SAMPLE_POLYGON,
        area_ha=2474.68,
        forest_type="Tropical Moist Broadleaf Forest",
        ecoregion="Central Amazon Moist Forests",
        canopy_cover_pct=88.5,
        mean_canopy_height_m=28.4,
        agb_t_per_ha=295.0,
        bgb_t_per_ha=70.8,
        total_biomass_t_per_ha=365.8,
        carbon_fraction=0.47,
        carbon_t_per_ha=171.93,
        co2e_t_per_ha=630.41,
        total_co2e=1560068.99,
        confidence_score=0.91,
        confidence_label="High",
        confidence_interval_pct=8.4,
        ndvi_trend="stable",
        data_sources=["sentinel-2", "gedi"],
        processing_time_seconds=0.72,
        data_mode=DataMode.MOCK,
        disclaimer="SIMULATED DATA (MOCK MODE): Generated for local testing. Estimates do not constitute verified carbon credits.",
    )


# --- 1. Saving an analysis ---


def test_save_analysis():
    """Verify save_analysis inserts a complete record with all required columns into Supabase."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.insert.return_value.execute.return_value = MagicMock(data=[{}])

    memory_repo = InMemoryAnalysisRepository()
    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=memory_repo,
        supabase_client=mock_supabase,
    )

    analysis = create_sample_analysis("save-test-001")
    result = db_service.save_analysis(analysis)

    assert result.analysis_id == "save-test-001"
    mock_supabase.table.assert_called_with(TABLE_NAME)

    # Check the record inserted into Supabase
    call_args = table_mock.insert.call_args[0][0]
    assert call_args["analysis_id"] == "save-test-001"
    assert call_args["area_ha"] == 2474.68
    assert call_args["forest_type"] == "Tropical Moist Broadleaf Forest"
    assert call_args["total_co2e"] == 1560068.99
    # Confidence score must be integer between 0 and 100
    assert call_args["confidence_score"] == 91
    assert call_args["data_mode"] == "mock"
    assert call_args["status"] == "complete"
    assert "full_response" in call_args
    assert call_args["full_response"]["analysis_id"] == "save-test-001"


# --- 2. Retrieving an existing analysis ---


def test_get_existing_analysis():
    """Verify retrieving an existing analysis returns the original full_response."""
    analysis = create_sample_analysis("retrieve-test-002")
    full_response_dict = analysis.model_dump(mode="json")

    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    (
        table_mock.select.return_value.eq.return_value.execute.return_value
    ) = MagicMock(data=[{"full_response": full_response_dict}])

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    retrieved = db_service.get_analysis_by_id("retrieve-test-002")
    assert retrieved is not None
    assert retrieved.analysis_id == "retrieve-test-002"
    assert retrieved.area_ha == 2474.68
    assert retrieved.total_co2e == 1560068.99
    assert retrieved.confidence_score == 0.91


# --- 3. Retrieving a missing analysis ---


def test_get_missing_analysis():
    """Verify retrieving an absent analysis returns None and triggers 404 in API."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

    empty_memory = InMemoryAnalysisRepository()
    empty_memory.clear()

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=empty_memory,
        supabase_client=mock_supabase,
    )

    result = db_service.get_analysis_by_id("non-existent-uuid-999")
    assert result is None

    # Test API endpoint returns 404 with analysis_not_found
    response = client.get("/api/analyze/non-existent-uuid-999")
    assert response.status_code == 404
    assert response.json()["error"] == "analysis_not_found"


# --- 4. Listing analyses ---


def test_list_analyses():
    """Verify list_analyses returns items ordered by newest first with all required summary fields."""
    sample_rows = [
        {
            "analysis_id": "row-001",
            "created_at": "2026-02-01T12:00:00+00:00",
            "area_ha": 500.5,
            "total_co2e": 315000.0,
            "forest_type": "Tropical Moist Broadleaf Forest",
            "confidence_score": 92,
            "status": "complete",
        },
        {
            "analysis_id": "row-002",
            "created_at": "2026-02-01T11:00:00+00:00",
            "area_ha": 300.0,
            "total_co2e": 189000.0,
            "forest_type": "Temperate Mixed Forest",
            "confidence_score": 85,
            "status": "complete",
        },
    ]

    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    (
        table_mock.select.return_value.order.return_value.range.return_value.execute.return_value
    ) = MagicMock(data=sample_rows)

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    summaries = db_service.list_analyses(limit=20, offset=0)
    assert len(summaries) == 2
    assert summaries[0].analysis_id == "row-001"
    assert summaries[0].confidence_score == 92
    assert summaries[0].status == "complete"
    assert summaries[1].analysis_id == "row-002"


# --- 5. Pagination ---


def test_pagination():
    """Verify limit and offset query parameters properly paginate through analyses."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock

    # Mock count
    table_mock.select.return_value.limit.return_value.execute.return_value = MagicMock(count=50, data=[])

    # Mock range
    range_mock = MagicMock()
    table_mock.select.return_value.order.return_value.range = range_mock
    range_mock.return_value.execute.return_value = MagicMock(data=[])

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    db_service.list_analyses(limit=15, offset=30)
    # Range is 0-indexed inclusive: [offset, offset + limit - 1] -> [30, 44]
    range_mock.assert_called_with(30, 44)


# --- 6. Empty database ---


def test_empty_database():
    """Verify empty database returns empty analyses list rather than raising an error."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.select.return_value.order.return_value.range.return_value.execute.return_value = MagicMock(data=[])
    table_mock.select.return_value.limit.return_value.execute.return_value = MagicMock(count=0, data=[])

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    summaries = db_service.list_analyses(limit=20, offset=0)
    count = db_service.count_analyses()

    assert summaries == []
    assert count == 0


# --- 7. Database unavailable ---


def test_database_unavailable():
    """Verify network failures or service unreachability raise DatabaseError without exposing credentials."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.insert.return_value.execute.side_effect = Exception("Supabase connection timed out / network down")

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    analysis = create_sample_analysis("fail-001")
    with pytest.raises(DatabaseError) as exc_info:
        db_service.save_analysis(analysis)

    assert "Database error" in str(exc_info.value.message)
    # Ensure secret credentials are never leaked
    assert "fake-secret-key" not in str(exc_info.value.message)


# --- 8. Mock mode without Supabase ---


def test_mock_mode_without_supabase():
    """Verify mock mode operates completely using in-memory store when Supabase credentials are unset."""
    memory_repo = InMemoryAnalysisRepository()
    memory_repo.clear()

    db_service = DatabaseService(
        settings=Settings(supabase_url=None, supabase_service_key=None, mock_mode=True),
        memory_repo=memory_repo,
        supabase_client=None,
    )

    assert not db_service.is_connected

    # Save
    analysis = create_sample_analysis("mem-001")
    saved = db_service.save_analysis(analysis)
    assert saved.analysis_id == "mem-001"

    # Retrieve
    retrieved = db_service.get_analysis_by_id("mem-001")
    assert retrieved is not None
    assert retrieved.analysis_id == "mem-001"

    # List
    summaries = db_service.list_analyses(limit=10, offset=0)
    assert len(summaries) == 1
    assert summaries[0].analysis_id == "mem-001"


# --- 9. Mock mode with Supabase ---


def test_mock_mode_with_supabase():
    """Verify mock mode when Supabase is available stores simulated results with data_mode='mock'."""
    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.insert.return_value.execute.return_value = MagicMock(data=[{}])

    db_service = DatabaseService(
        settings=Settings(
            supabase_url="https://example.supabase.co",
            supabase_service_key="fake-secret-key",
            mock_mode=True,
        ),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    assert db_service.is_connected

    analysis = create_sample_analysis("mock-supa-001")
    assert analysis.data_mode == DataMode.MOCK

    db_service.save_analysis(analysis)

    call_args = table_mock.insert.call_args[0][0]
    assert call_args["data_mode"] == "mock"
    assert "SIMULATED DATA" in call_args["full_response"]["disclaimer"]


# --- 10. Preservation of complete response data ---


def test_preservation_of_complete_response_data():
    """Verify no scientific, provenance, or ecological metrics are discarded when saving and retrieving."""
    original_analysis = create_sample_analysis("complete-data-001")
    original_json = original_analysis.model_dump(mode="json")

    mock_supabase = MagicMock()
    table_mock = MagicMock()
    mock_supabase.table.return_value = table_mock
    table_mock.insert.return_value.execute.return_value = MagicMock(data=[{}])
    table_mock.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{"full_response": original_json}]
    )

    db_service = DatabaseService(
        settings=Settings(supabase_url="https://example.supabase.co", supabase_service_key="fake-secret-key"),
        memory_repo=InMemoryAnalysisRepository(),
        supabase_client=mock_supabase,
    )

    # Save
    db_service.save_analysis(original_analysis)
    saved_record = table_mock.insert.call_args[0][0]

    # Verify full_response in inserted payload contains all fields
    saved_full = saved_record["full_response"]
    for field_name in [
        "analysis_id",
        "timestamp",
        "polygon",
        "area_ha",
        "forest_type",
        "ecoregion",
        "canopy_cover_pct",
        "mean_canopy_height_m",
        "agb_t_per_ha",
        "bgb_t_per_ha",
        "total_biomass_t_per_ha",
        "carbon_fraction",
        "carbon_t_per_ha",
        "co2e_t_per_ha",
        "total_co2e",
        "confidence_score",
        "confidence_label",
        "confidence_interval_pct",
        "ndvi_trend",
        "data_sources",
        "processing_time_seconds",
        "data_mode",
        "disclaimer",
    ]:
        assert field_name in saved_full, f"Missing field {field_name} in full_response"

    # Retrieve
    retrieved = db_service.get_analysis_by_id("complete-data-001")
    retrieved_json = retrieved.model_dump(mode="json")

    # Verify retrieved object matches original
    assert retrieved_json == original_json
