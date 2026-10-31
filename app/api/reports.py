"""PDF Report download API endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.models.schemas import ErrorResponse
from app.services.pdf_service import PDFService, pdf_service

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
    },
)
async def download_report(
    analysis_id: str,
    service: PDFService = Depends(lambda: pdf_service),
) -> StreamingResponse:
    """Generate and stream a PDF summary report for a given analysis ID."""
    pdf_buffer = service.generate_report_by_id(analysis_id)
    filename = f"canopyai-report-{analysis_id}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )
