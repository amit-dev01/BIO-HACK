-- CanopyAI Supabase Database Schema
-- Table: analyses
-- Purpose: Persist forest carbon and biomass analyses computed from satellite data or simulation.

CREATE TABLE IF NOT EXISTS public.analyses (
    analysis_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    polygon_geojson JSONB NOT NULL,
    area_ha DOUBLE PRECISION NOT NULL,
    forest_type TEXT,
    total_co2e DOUBLE PRECISION,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    data_mode TEXT NOT NULL CHECK (data_mode IN ('mock', 'satellite')),
    full_response JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'complete' CHECK (status IN ('complete', 'failed'))
);

-- Index for ordering by creation timestamp (newest first)
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses (created_at DESC);

-- Comments for database documentation
COMMENT ON TABLE public.analyses IS 'Forest biomass and carbon storage analysis records';
COMMENT ON COLUMN public.analyses.analysis_id IS 'Unique UUID4 identifier for the analysis';
COMMENT ON COLUMN public.analyses.created_at IS 'UTC timestamp when analysis was generated';
COMMENT ON COLUMN public.analyses.polygon_geojson IS 'Evaluated GeoJSON Polygon geometry';
COMMENT ON COLUMN public.analyses.area_ha IS 'Calculated forest surface area in hectares';
COMMENT ON COLUMN public.analyses.forest_type IS 'Dominant biome/forest classification';
COMMENT ON COLUMN public.analyses.total_co2e IS 'Total estimated CO2 equivalent in tonnes';
COMMENT ON COLUMN public.analyses.confidence_score IS 'Model confidence integer grade (0 to 100)';
COMMENT ON COLUMN public.analyses.data_mode IS 'Data provenance: mock (simulated) or satellite (live)';
COMMENT ON COLUMN public.analyses.full_response IS 'Complete, uncompressed JSON analysis response payload';
COMMENT ON COLUMN public.analyses.status IS 'Processing lifecycle state: complete or failed';
