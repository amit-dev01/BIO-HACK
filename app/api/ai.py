"""FastAPI router for Gemini AI ecological narratives and interactive Q&A."""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.services.analysis_service import AnalysisService, analysis_service
from app.services.gemini_service import GeminiService, gemini_service

logger = logging.getLogger("canopyai.api.ai")

router = APIRouter(prefix="/ai", tags=["AI Intelligence (Gemini 3.8 Flash)"])


class NarrativeRequest(BaseModel):
    analysis_id: Optional[str] = Field(default=None, description="Optional ID of existing analysis to generate narrative for")
    analysis_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional raw analysis telemetry object")


class ChatRequest(BaseModel):
    analysis_id: Optional[str] = Field(default=None, description="Analysis ID for grounding context")
    analysis_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional raw analysis telemetry object")
    question: str = Field(..., description="User question about the forest")
    previous_interaction_id: Optional[str] = Field(default=None, description="Optional previous Gemini interaction ID for multi-turn stateful conversation")


@router.post(
    "/narrative",
    summary="Generate Gemini 3.8 Flash Ecological Audit Narrative",
    description="Synthesize satellite telemetry into an authoritative executive carbon audit narrative using Google Gemini 3.8 Flash.",
)
async def generate_narrative(
    request: NarrativeRequest,
    analysis_srv: AnalysisService = Depends(lambda: analysis_service),
    gemini_srv: GeminiService = Depends(lambda: gemini_service),
) -> Dict[str, Any]:
    telemetry: Dict[str, Any] = {}

    if request.analysis_data:
        telemetry = request.analysis_data
    elif request.analysis_id:
        try:
            analysis = analysis_srv.get_analysis_by_id(request.analysis_id)
            telemetry = analysis.model_dump(mode="json")
        except Exception as exc:
            logger.warning("Could not fetch analysis %s for narrative: %s", request.analysis_id, exc)
            telemetry = {"analysis_id": request.analysis_id}

    if not telemetry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either analysis_id or analysis_data must be provided.",
        )

    narrative = gemini_srv.generate_ecological_narrative(telemetry)
    return {"status": "ok", "narrative": narrative}


@router.post(
    "/chat",
    summary="Conversational Forest Q&A via Gemini 3.8 Flash",
    description="Ask natural-language questions about an analyzed forest with grounded spaceborne telemetry context.",
)
async def chat_forest(
    request: ChatRequest,
    analysis_srv: AnalysisService = Depends(lambda: analysis_service),
    gemini_srv: GeminiService = Depends(lambda: gemini_service),
) -> Dict[str, Any]:
    telemetry: Dict[str, Any] = {}

    if request.analysis_data:
        telemetry = request.analysis_data
    elif request.analysis_id:
        try:
            analysis = analysis_srv.get_analysis_by_id(request.analysis_id)
            telemetry = analysis.model_dump(mode="json")
        except Exception:
            telemetry = {"analysis_id": request.analysis_id}

    result = gemini_srv.chat_with_forest(
        analysis_data=telemetry,
        user_message=request.question,
        previous_interaction_id=request.previous_interaction_id,
    )
    return {"status": "ok", **result}

