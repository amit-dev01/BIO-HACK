"""PDF Report generation service for CanopyAI using ReportLab.

Renders forest biomass and carbon storage assessment summaries into downloadable
PDF documents.
"""

from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.schemas import AnalysisResponse
from app.services.mock_service import mock_repository
from app.utils.errors import AnalysisNotFoundError


class PDFService:
    """Generates standardized PDF summary reports from forest carbon analyses."""

    def __init__(self) -> None:
        pass

    def generate_report(self, analysis: AnalysisResponse) -> BytesIO:
        """Generate a binary PDF document buffer for the provided analysis."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleStyle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1b4d3e"),  # Forest Green
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            name="SubtitleStyle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#4a5568"),
            spaceAfter=15,
        )

        header_style = ParagraphStyle(
            name="HeaderStyle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2d3748"),
            spaceBefore=10,
            spaceAfter=8,
        )

        cell_bold = ParagraphStyle(
            name="CellBold",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#2d3748"),
        )

        cell_normal = ParagraphStyle(
            name="CellNormal",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4a5568"),
        )

        disclaimer_style = ParagraphStyle(
            name="DisclaimerStyle",
            parent=styles["Italic"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#718096"),
            spaceBefore=15,
        )

        story = []

        # Header Title
        story.append(Paragraph("CanopyAI — Forest Carbon & Biomass Assessment", title_style))
        mode_label = "[SIMULATED / MOCK DATA]" if analysis.data_mode == "mock" else "[SATELLITE DATA]"
        story.append(
            Paragraph(
                f"Generated on: {analysis.timestamp.strftime('%Y-%m-%d %H:%M UTC')} &bull; Status: {mode_label}",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 10))

        # Project & Location Summary Table
        story.append(Paragraph("1. Location & Region Profile", header_style))
        loc_data = [
            [Paragraph("Analysis ID", cell_bold), Paragraph(analysis.analysis_id, cell_normal)],
            [Paragraph("Area (hectares)", cell_bold), Paragraph(f"{analysis.area_ha:,.2f} ha", cell_normal)],
            [Paragraph("Forest Type", cell_bold), Paragraph(analysis.forest_type or "Unclassified", cell_normal)],
            [Paragraph("Ecoregion", cell_bold), Paragraph(analysis.ecoregion or "Unclassified", cell_normal)],
            [
                Paragraph("Data Sources", cell_bold),
                Paragraph(", ".join(analysis.data_sources) if analysis.data_sources else "N/A", cell_normal),
            ],
        ]
        t1 = Table(loc_data, colWidths=[160, 380])
        t1.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t1)
        story.append(Spacer(1, 15))

        # Biomass & Carbon Table
        story.append(Paragraph("2. Biomass & Carbon Estimation Metrics", header_style))
        metrics_data = [
            [
                Paragraph("Metric", cell_bold),
                Paragraph("Estimated Value", cell_bold),
                Paragraph("Standard Unit", cell_bold),
            ],
            [
                Paragraph("Canopy Cover", cell_normal),
                Paragraph(f"{analysis.canopy_cover_pct:.1f}%" if analysis.canopy_cover_pct is not None else "N/A", cell_normal),
                Paragraph("percentage (%)", cell_normal),
            ],
            [
                Paragraph("Mean Canopy Height", cell_normal),
                Paragraph(f"{analysis.mean_canopy_height_m:.1f} m" if analysis.mean_canopy_height_m is not None else "N/A", cell_normal),
                Paragraph("meters (m)", cell_normal),
            ],
            [
                Paragraph("Above-ground Biomass (AGB)", cell_normal),
                Paragraph(f"{analysis.agb_t_per_ha:,.2f}" if analysis.agb_t_per_ha is not None else "N/A", cell_normal),
                Paragraph("tonnes/hectare", cell_normal),
            ],
            [
                Paragraph("Below-ground Biomass (BGB)", cell_normal),
                Paragraph(f"{analysis.bgb_t_per_ha:,.2f}" if analysis.bgb_t_per_ha is not None else "N/A", cell_normal),
                Paragraph("tonnes/hectare", cell_normal),
            ],
            [
                Paragraph("Total Biomass", cell_bold),
                Paragraph(f"{analysis.total_biomass_t_per_ha:,.2f}" if analysis.total_biomass_t_per_ha is not None else "N/A", cell_bold),
                Paragraph("tonnes/hectare", cell_normal),
            ],
            [
                Paragraph("Carbon Stock Density", cell_bold),
                Paragraph(f"{analysis.carbon_t_per_ha:,.2f}" if analysis.carbon_t_per_ha is not None else "N/A", cell_bold),
                Paragraph("tonnes C/hectare", cell_normal),
            ],
            [
                Paragraph("CO2 Equivalent Density", cell_normal),
                Paragraph(f"{analysis.co2e_t_per_ha:,.2f}" if analysis.co2e_t_per_ha is not None else "N/A", cell_normal),
                Paragraph("tonnes CO2e/hectare", cell_normal),
            ],
            [
                Paragraph("Total Estimated CO2e Stock", cell_bold),
                Paragraph(f"{analysis.total_co2e:,.2f}" if analysis.total_co2e is not None else "N/A", cell_bold),
                Paragraph("tonnes CO2e (total area)", cell_normal),
            ],
            [
                Paragraph("Confidence Grade", cell_normal),
                Paragraph(f"{analysis.confidence_label} ({analysis.confidence_score*100:.1f}%)" if analysis.confidence_score is not None else "N/A", cell_normal),
                Paragraph(f"Interval: &plusmn;{analysis.confidence_interval_pct:.1f}%" if analysis.confidence_interval_pct is not None else "-", cell_normal),
            ],
        ]
        t2 = Table(metrics_data, colWidths=[200, 170, 170])
        t2.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(t2)
        story.append(Spacer(1, 15))

        # Regulatory & Scientific Disclaimer
        story.append(Paragraph("Regulatory Notice & Scientific Disclaimer", header_style))
        story.append(Paragraph(analysis.disclaimer, disclaimer_style))
        story.append(
            Paragraph(
                "Notice: Estimates provided herein are derived from satellite remote sensing observations and biophysical modeling. "
                "They are intended solely for environmental monitoring, conservation planning, and ecological assessment. "
                "These figures do NOT represent verified, certified, or tradeable carbon offsets/credits under Verra, Gold Standard, "
                "or other regulatory carbon crediting mechanisms.",
                disclaimer_style,
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_report_by_id(self, analysis_id: str) -> BytesIO:
        """Fetch analysis by ID and generate its PDF report."""
        analysis = mock_repository.get_by_id(analysis_id)
        if not analysis:
            raise AnalysisNotFoundError(analysis_id=analysis_id)
        return self.generate_report(analysis)


# Global service instance
pdf_service = PDFService()
