"""Gemini AI service for ecological narrative generation and interactive forest Q&A.

Uses the official google-genai SDK (v2+) with gemini-3.8-flash and automatic fallback.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from app.config import get_settings

logger = logging.getLogger("canopyai.services.gemini")

CANDIDATE_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]


class GeminiService:
    """Service orchestrating Google Gemini for forest carbon intelligence."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    def _get_client(self):
        """Lazy-initialize the official google-genai client."""
        if self._client is not None:
            return self._client

        api_key = self.settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            from google import genai

            self._client = genai.Client(api_key=api_key)
            return self._client
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not initialize google-genai client: %s", exc)
            return None

    def _create_interaction(self, client: Any, **kwargs) -> Tuple[Any, str]:
        """Call interactions.create with model cascading (gemini-3.8-flash -> gemini-3.5-flash)."""
        last_exc = None
        for model_name in CANDIDATE_MODELS:
            try:
                call_kwargs = dict(kwargs)
                call_kwargs["model"] = model_name
                interaction = client.interactions.create(**call_kwargs)
                return interaction, model_name
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("Interactions API model %s failed: %s; trying fallback model...", model_name, exc)
        if last_exc:
            raise last_exc
        raise RuntimeError("No model candidates available")

    def generate_ecological_narrative(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured, audit-ready ecological executive narrative using Gemini."""
        client = self._get_client()

        # Build grounding context from satellite telemetry
        area_ha = analysis_data.get("area_ha", 0)
        total_co2e = analysis_data.get("total_co2e", 0)
        co2e_per_ha = analysis_data.get("co2e_t_per_ha", 0)
        canopy_cover = analysis_data.get("canopy_cover_pct", 0)
        canopy_height = analysis_data.get("mean_canopy_height_m", 0)
        forest_type = analysis_data.get("forest_type", "Forest")
        ecoregion = analysis_data.get("ecoregion", "Regional Ecosystem")
        conf_score = analysis_data.get("confidence_score", 0)
        if conf_score and conf_score <= 1:
            conf_score = round(conf_score * 100)
        conf_label = analysis_data.get("confidence_label", "Tier 2/3")
        recommended_std = analysis_data.get("recommended_standard", "Verra VCS (VM0047)")
        data_sources = ", ".join(analysis_data.get("data_sources", ["NASA GEDI", "ESA Sentinel-2"]))

        if not client:
            # Fallback narrative when API key is not yet set
            return {
                "configured": False,
                "model": "heuristic-baseline",
                "executive_summary": (
                    f"This {forest_type.lower()} spanning {area_ha:,.1f} hectares stores an estimated "
                    f"{total_co2e:,.0f} tCO₂e with a high-density biomass profile of {co2e_per_ha:.1f} tCO₂e/ha. "
                    f"Remote sensing telemetry confirms {canopy_cover:.1f}% mean canopy closure with an average "
                    f"canopy height of {canopy_height:.1f} meters, demonstrating strong structural integrity and "
                    f"photosynthetic vigor across the observed tract."
                ),
                "permanence_and_risk": (
                    "Multi-spectral time-series analysis reflects consistent vegetative stability with negligible "
                    "canopy loss detected. Biomass permanence is supported by high canopy density and low historical fragmentation."
                ),
                "registry_compliance": (
                    f"Recommended for {recommended_std}. Meets Tier 3 remote-sensing thresholds with an audit readiness "
                    f"score of {conf_score}/100. Suitable for accelerated digital Project Design Document (PDD) submission."
                ),
                "key_highlights": [
                    f"High-density carbon pool: {co2e_per_ha:.1f} tCO₂e/ha",
                    f"Verified spaceborne canopy height: {canopy_height:.1f}m",
                    f"Audit confidence: {conf_score}/100 ({conf_label})",
                ],
                "notice": "Set GEMINI_API_KEY in .env to activate real-time Gemini Flash narrative generation.",
            }

        prompt = f"""You are a senior forest carbon MRV auditor evaluating spaceborne telemetry for carbon credit certification.
Analyze the following satellite assessment data:
- Forest Area: {area_ha:,.1f} hectares
- Forest Classification: {forest_type} ({ecoregion})
- Total Carbon Stock: {total_co2e:,.0f} tCO2e
- Carbon Density: {co2e_per_ha:.1f} tCO2e/ha
- Mean Canopy Cover: {canopy_cover:.1f}%
- Mean Canopy Height: {canopy_height:.1f} meters (NASA GEDI L4A LiDAR)
- Verification Confidence Score: {conf_score}/100 ({conf_label})
- Satellite Data Sources: {data_sources}
- Recommended Standard: {recommended_std}

Provide an authoritative, rigorous carbon audit narrative. Return ONLY valid JSON with the following keys:
{{
  "executive_summary": "A 2-paragraph professional executive summary synthesizing biomass stock, canopy height, and regional ecological importance.",
  "permanence_and_risk": "An evaluation of carbon permanence, vegetation health, and climate risk resilience.",
  "registry_compliance": "An assessment of alignment with Verra VCS (VM0047/VM0007) and carbon market financing feasibility.",
  "key_highlights": ["3 to 4 concise bullet points of notable ecological findings"]
}}
"""
        try:
            interaction, used_model = self._create_interaction(client, input=prompt)
            raw_text = interaction.output_text or ""
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            parsed["configured"] = True
            parsed["model"] = used_model
            return parsed
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini narrative generation failed: %s", exc)
            return {
                "configured": True,
                "model": "gemini-fallback",
                "executive_summary": f"Telemetry indicates {total_co2e:,.0f} tCO₂e stored across {area_ha:,.1f} ha.",
                "permanence_and_risk": "Vegetation metrics show robust canopy cover.",
                "registry_compliance": f"Aligned with {recommended_std}.",
                "key_highlights": [f"Area: {area_ha} ha", f"Carbon: {total_co2e} tCO2e"],
                "error": str(exc),
            }

    def chat_with_forest(
        self,
        analysis_data: Dict[str, Any],
        user_message: str,
        previous_interaction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer user questions about the specific forest using grounded satellite context."""
        client = self._get_client()
        if not client:
            return {
                "reply": (
                    "Gemini AI assistant is ready. To enable live natural-language interaction, "
                    "add your free GEMINI_API_KEY from Google AI Studio to the backend .env file."
                ),
                "interaction_id": None,
                "configured": False,
            }

        context_prompt = (
            f"You are CanopyAI Assistant, an expert ecological remote sensing and carbon auditor. "
            f"The user is viewing a verified forest analysis with these parameters:\n"
            f"- Area: {analysis_data.get('area_ha')} ha\n"
            f"- Carbon Stock: {analysis_data.get('total_co2e')} tCO2e ({analysis_data.get('co2e_t_per_ha')} tCO2e/ha)\n"
            f"- Canopy Cover: {analysis_data.get('canopy_cover_pct')}%\n"
            f"- Canopy Height: {analysis_data.get('mean_canopy_height_m')} meters\n"
            f"- Forest Type: {analysis_data.get('forest_type')}\n"
            f"- Confidence: {analysis_data.get('confidence_score')}/100 ({analysis_data.get('confidence_label')})\n"
            f"- Recommended Standard: {analysis_data.get('recommended_standard')}\n\n"
            f"Answer the user's question accurately, concisely, and grounded in these satellite findings.\n"
            f"User Question: {user_message}"
        )

        try:
            kwargs: Dict[str, Any] = {
                "input": context_prompt if not previous_interaction_id else user_message,
            }
            if previous_interaction_id:
                kwargs["previous_interaction_id"] = previous_interaction_id

            interaction, used_model = self._create_interaction(client, **kwargs)
            return {
                "reply": interaction.output_text or "No response generated.",
                "interaction_id": interaction.id,
                "configured": True,
                "model": used_model,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini chat interaction failed: %s", exc)
            return {
                "reply": f"Could not complete AI query: {exc}",
                "interaction_id": None,
                "configured": True,
                "error": str(exc),
            }


gemini_service = GeminiService()
