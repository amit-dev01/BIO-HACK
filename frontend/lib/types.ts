export type PolygonData = GeoJSON.Feature<GeoJSON.Polygon>;

export interface NdviDataPoint {
  quarter: string;
  ndvi: number;
}

export interface AnalysisResult {
  analysis_id: string;
  timestamp: string;
  polygon: PolygonData;
  area_ha: number;
  forest_type: string;
  ecoregion: string;
  canopy_cover_pct: number;
  mean_canopy_height_m: number;
  agb_t_per_ha: number;
  bgb_t_per_ha: number;
  total_biomass_t_per_ha: number;
  carbon_fraction: number;
  carbon_t_per_ha: number;
  co2e_t_per_ha: number;
  total_co2e: number;
  confidence_score: number;
  confidence_label: string;
  confidence_interval_pct: number;
  annual_sequestration_tco2e: number;
  credit_revenue_estimate_usd: number;
  credit_price_assumption_usd: number;
  recommended_standard: string;
  ndvi_trend: NdviDataPoint[];
  data_sources: string[];
  deforestation_alert: boolean;
  tree_cover_loss_pct_5yr: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string;
  created_at: string;
}

export interface SavedAnalysis {
  id: string;
  user_id: string;
  analysis_result: AnalysisResult;
  created_at: string;
  location_name: string;
  status: "complete" | "pending" | "processing" | "failed" | string;
}

export interface AnalysisConfig {
  data_sources: string[];
  analysis_type: "quick" | "detailed";
  drone_image: File | null;
}

export type AnalysisStatus =
  | "idle"
  | "drawing"
  | "configuring"
  | "loading"
  | "complete"
  | "error";

export interface ProgressStep {
  step_number: number;
  label: string;
  duration_ms: number;
  status: "pending" | "active" | "complete";
}

