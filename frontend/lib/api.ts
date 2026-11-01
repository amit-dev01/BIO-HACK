import { AnalysisResult, PolygonData } from "./types";
import { mockNdviTrend } from "./mock-data";

export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (
    typeof window !== "undefined" &&
    (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ) {
    return "http://localhost:8000";
  }
  return "https://bio-hack.onrender.com";
}

const API_BASE_URL = getApiBaseUrl();

// Normalizes backend API response into frontend AnalysisResult
export function normalizeAnalysisResponse(
  raw: any,
  fallbackPolygon?: PolygonData
): AnalysisResult {
  // Normalize polygon into GeoJSON Feature
  let normalizedPolygon: PolygonData = fallbackPolygon || { type: "Feature", properties: { name: raw.forest_type || "Analyzed Area" }, geometry: raw.polygon || { type: "Polygon", coordinates: [] } };
  if (raw.polygon) {
    if (raw.polygon.type === "Feature") {
      normalizedPolygon = raw.polygon;
    } else if (raw.polygon.type === "Polygon") {
      normalizedPolygon = {
        type: "Feature",
        properties: { name: raw.forest_type || "Analyzed Forest Area" },
        geometry: raw.polygon,
      };
    }
  }

  // Handle confidence score (convert 0-1 range to 0-100 if needed)
  let score = typeof raw.confidence_score === "number" ? raw.confidence_score : 85;
  if (score > 0 && score <= 1) {
    score = Math.round(score * 100);
  }

  // Handle annual sequestration and credit estimate if not explicitly provided
  const area = raw.area_ha ?? 1000;
  const totalCo2e = raw.total_co2e ?? area * 500;
  const annualSeq =
    raw.annual_sequestration_tco2e ??
    Math.round(totalCo2e * 0.012 || area * 6.6);
  const creditPrice = raw.credit_price_assumption_usd ?? 15.0;
  const creditRev =
    raw.credit_revenue_estimate_usd ?? Math.round(annualSeq * creditPrice);

  // Handle NDVI trend (ensure array for chart)
  const ndviTrend =
    Array.isArray(raw.ndvi_trend) && raw.ndvi_trend.length > 0
      ? raw.ndvi_trend
      : mockNdviTrend;

  return {
    analysis_id: raw.analysis_id || `cai_${Date.now()}`,
    timestamp: raw.timestamp || new Date().toISOString(),
    polygon: normalizedPolygon,
    area_ha: Number(area.toFixed ? area.toFixed(1) : area),
    forest_type: raw.forest_type || "Tropical Moist Broadleaf Forest",
    ecoregion: raw.ecoregion || "Equatorial Moist Forest Biome",
    canopy_cover_pct: Number((raw.canopy_cover_pct ?? 88.5).toFixed ? (raw.canopy_cover_pct ?? 88.5).toFixed(1) : 88.5),
    mean_canopy_height_m: Number((raw.mean_canopy_height_m ?? 28.5).toFixed ? (raw.mean_canopy_height_m ?? 28.5).toFixed(1) : 28.5),
    agb_t_per_ha: Number((raw.agb_t_per_ha ?? 260.0).toFixed ? (raw.agb_t_per_ha ?? 260.0).toFixed(1) : 260.0),
    bgb_t_per_ha: Number((raw.bgb_t_per_ha ?? 52.0).toFixed ? (raw.bgb_t_per_ha ?? 52.0).toFixed(1) : 52.0),
    total_biomass_t_per_ha: Number((raw.total_biomass_t_per_ha ?? 312.0).toFixed ? (raw.total_biomass_t_per_ha ?? 312.0).toFixed(1) : 312.0),
    carbon_fraction: raw.carbon_fraction ?? 0.47,
    carbon_t_per_ha: Number((raw.carbon_t_per_ha ?? 146.6).toFixed ? (raw.carbon_t_per_ha ?? 146.6).toFixed(1) : 146.6),
    co2e_t_per_ha: Number((raw.co2e_t_per_ha ?? 538.0).toFixed ? (raw.co2e_t_per_ha ?? 538.0).toFixed(1) : 538.0),
    total_co2e: Number(totalCo2e.toFixed ? totalCo2e.toFixed(1) : totalCo2e),
    confidence_score: score,
    confidence_label:
      raw.confidence_label || (score >= 85 ? "High (Tier 3)" : "Moderate (Tier 2)"),
    confidence_interval_pct: raw.confidence_interval_pct ?? 14.5,
    annual_sequestration_tco2e: annualSeq,
    credit_revenue_estimate_usd: creditRev,
    credit_price_assumption_usd: creditPrice,
    recommended_standard:
      raw.recommended_standard || "Verra VCS (VM0047 / VM0007)",
    ndvi_trend: ndviTrend,
    data_sources: Array.isArray(raw.data_sources)
      ? raw.data_sources
      : ["Sentinel-2 MSI", "NASA GEDI L4A", "ALOS PALSAR-2"],
    deforestation_alert: !!raw.deforestation_alert,
    tree_cover_loss_pct_5yr: raw.tree_cover_loss_pct_5yr ?? 0.45,
  };
}

export const api = {
  // Check backend health
  async checkHealth() {
    const res = await fetch(`${getApiBaseUrl()}/api/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  // Post polygon for analysis
  async analyze(polygon: PolygonData, dataSources?: string[], analysisType?: string) {
    // Backend expects GeoJSON polygon geometry
    const geometry = polygon.geometry || polygon;
    const payload = {
      polygon: geometry,
      data_sources: dataSources || ["sentinel-2", "gedi"],
      analysis_type: analysisType || "detailed",
    };

    const res = await fetch(`${getApiBaseUrl()}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg =
        err.message ||
        err.detail ||
        (typeof err.error === "string" ? err.error : null) ||
        `Analysis failed (${res.status})`;
      throw new Error(msg);
    }

    const data = await res.json();
    return normalizeAnalysisResponse(data, polygon);
  },

  // Get single analysis by ID
  async getAnalysisById(id: string): Promise<AnalysisResult> {
    const res = await fetch(`${getApiBaseUrl()}/api/analyze/${id}`);
    if (!res.ok) {
      throw new Error(`Analysis not found: ${res.status}`);
    }
    const data = await res.json();
    return normalizeAnalysisResponse(data);
  },

  // List analyses history
  async listAnalyses(limit = 20, offset = 0) {
    const res = await fetch(
      `${getApiBaseUrl()}/api/analyses?limit=${limit}&offset=${offset}`
    );
    if (!res.ok) {
      throw new Error(`Failed to list analyses: ${res.status}`);
    }
    return res.json();
  },

  // Get download report URL
  getReportPdfUrl(analysisId: string) {
    return `${getApiBaseUrl()}/api/reports/${analysisId}/download`;
  },

  // Upload drone image
  async uploadDroneImage(file: File) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${getApiBaseUrl()}/api/drone/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error(`Drone upload failed: ${res.statusText}`);
    }
    return res.json();
  },
};

