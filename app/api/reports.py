"""PDF Report download API endpoints."""

from io import BytesIO
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.models.schemas import ErrorResponse
from app.services.database_service import DatabaseService, database_service
from app.services.pdf_service import generate_pdf_report
from app.utils.errors import AnalysisNotFoundError

logger = logging.getLogger("canopyai.reports")

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/{analysis_id}/download",
    response_class=StreamingResponse,
    summary="Download Analysis PDF Report",
    description="Generate and download a comprehensive PDF report summarizing the carbon and biomass analysis.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Binary PDF document stream for download",
        },
        404: {"model": ErrorResponse, "description": "Analysis not found"},
        500: {"model": ErrorResponse, "description": "PDF generation failed"},
    },
)
async def download_report(
    analysis_id: str,
    db_service: DatabaseService = Depends(lambda: database_service),
) -> Any:
    """Generate and stream a PDF summary report for a given analysis ID."""
    # 1. Retrieve analysis from database/in-memory repository
    analysis = db_service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise AnalysisNotFoundError(analysis_id=analysis_id)

    # 2. Extract full_response dictionary from stored analysis
    if hasattr(analysis, "model_dump"):
        full_response: Dict[str, Any] = analysis.model_dump(mode="json")
    elif isinstance(analysis, dict):
        full_response = analysis.get("full_response", analysis)
    else:
        full_response = dict(analysis)

    # 3. Generate the PDF bytes in memory
    try:
        pdf_bytes = generate_pdf_report(full_response)
    except Exception as e:
        logger.error("PDF generation failed for analysis %s: %s", analysis_id, str(e), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "report_generation_failed",
                "message": "Unable to generate PDF report.",
            },
        )

    # 4. Stream response with required headers
    filename = f"canopyai_report_{analysis_id}.pdf"
    content_disposition = f'attachment; filename="{filename}"; filename*="canopyai-report-{analysis_id}.pdf"'

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Type": "application/pdf",
            "Content-Disposition": content_disposition,
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
