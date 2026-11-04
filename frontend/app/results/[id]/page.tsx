"use client";

import React, { useEffect, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

import { StatCard } from "@/components/results/StatCard";
import { ResultsHeader } from "@/components/results/ResultsHeader";
import { ResultsMap } from "@/components/results/ResultsMap";
import { ForestTable } from "@/components/results/ForestTable";
import { CarbonPotential } from "@/components/results/CarbonPotential";
import { NdviChart } from "@/components/results/NdviChart";
import { Methodology } from "@/components/results/Methodology";
import { SpaceborneTelemetry } from "@/components/results/SpaceborneTelemetry";
import { ExportReportButton } from "@/components/results/ExportReportButton";
import { AiEcologicalSummary } from "@/components/results/AiEcologicalSummary";
import {
  TreePine,
  Download,
  Share2,
  ArrowLeft,
  ShieldCheck,
  Sparkles,
  BarChart3,
  Calendar,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";
import { Button } from "@/components/ui/button";
import { AnalysisResult, PolygonData } from "@/lib/types";
import { api } from "@/lib/api";

export default function ResultsPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = (params?.id as string) || "cai_anlz_20241031_001";
  const { state } = useAnalysis();
  const [fetchedResult, setFetchedResult] = React.useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = React.useState(!state.results || state.results.analysis_id !== analysisId);
  const [fetchError, setFetchError] = React.useState<string | null>(null);

  // Fetch from real backend if id does not match current state
  React.useEffect(() => {
    if (state.results && state.results.analysis_id === analysisId) {
      setFetchedResult(state.results);
      setIsLoading(false);
      return;
    }

    let isMounted = true;
    setIsLoading(true);
    setFetchError(null);

    api
      .getAnalysisById(analysisId)
      .then((data) => {
        if (isMounted) {
          setFetchedResult(data);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.warn("Could not fetch analysis from backend:", err);
          setFetchError(err instanceof Error ? err.message : "Analysis record not found");
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [analysisId, state.results]);

  const result: AnalysisResult | null = useMemo(() => {
    if (state.results && state.results.analysis_id === analysisId) {
      return state.results;
    }
    return fetchedResult;
  }, [state.results, fetchedResult, analysisId]);

  const polygon: PolygonData = useMemo(() => {
    if (state.polygon) {
      return state.polygon;
    }
    if (result?.polygon) {
      return result.polygon;
    }
    return {
      type: "Feature",
      properties: { name: result?.forest_type || "Analyzed Area" },
      geometry: { type: "Polygon", coordinates: [] },
    };
  }, [state.polygon, result?.polygon, result?.forest_type]);

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50 text-gray-900">
        <Navbar />
        <main className="flex-1 flex flex-col items-center justify-center p-8 space-y-4">
          <Loader2 className="w-10 h-10 animate-spin text-green-600" />
          <h2 className="text-xl font-bold text-gray-800">Loading Satellite Analysis...</h2>
          <p className="text-xs text-gray-500 font-mono">Fetching assessment records for {analysisId}</p>
        </main>
        <Footer />
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50 text-gray-900">
        <Navbar />
        <main className="flex-1 max-w-lg mx-auto flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-8 text-center shadow-xl border border-gray-100 space-y-5">
            <div className="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-8 h-8 text-amber-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Analysis Not Found</h2>
              <p className="text-sm text-gray-500 mt-1">
                No live analysis was found for ID:{" "}
                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs font-mono">{analysisId}</code>
              </p>
              {fetchError && (
                <p className="text-xs text-red-600 mt-2 bg-red-50 p-2 rounded-xl border border-red-200">
                  {fetchError}
                </p>
              )}
            </div>
            <Button asChild className="bg-green-600 hover:bg-green-700 text-white rounded-full px-6">
              <Link href="/analyze">
                <ArrowLeft className="w-4 h-4 mr-2" /> Select Forest on Map
              </Link>
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 text-gray-900">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Navigation & Breadcrumbs */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Link
              href="/analyze"
              className="inline-flex items-center gap-1.5 hover:text-green-700 transition-colors font-medium"
            >
              <ArrowLeft className="w-4 h-4" /> Back to Map
            </Link>
            <span>/</span>
            <span className="font-mono text-xs text-gray-700">{analysisId}</span>
          </div>

          <div className="flex items-center gap-3">
            <ExportReportButton result={result} />
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (navigator.clipboard) {
                  navigator.clipboard.writeText(window.location.href);
                  alert("Report URL copied to clipboard!");
                }
              }}
              className="gap-1.5"
            >
              <Share2 className="w-4 h-4" /> Share
            </Button>
            <Button
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white gap-1.5"
              asChild
            >
              <Link href="/analyze">
                <TreePine className="w-4 h-4" /> New Analysis
              </Link>
            </Button>
          </div>
        </div>

        {/* Results Header */}
        <ResultsHeader result={result} />

        {/* Stat Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Carbon Stock"
            value={Math.round(result.total_co2e)}
            unit="tCO₂e"
            subtitle={result.confidence_interval_pct ? `±${result.confidence_interval_pct}% uncertainty range` : "IPCC Tier 2/3 verified"}
            icon={TreePine}
            isCarbon
            trend={{
              direction: "up",
              text: `+${(result.annual_sequestration_tco2e ?? Math.round(result.total_co2e * 0.012)).toLocaleString()} t/yr`,
            }}
          />

          <StatCard
            title="Carbon Density"
            value={(result.co2e_t_per_ha ?? (result.area_ha ? result.total_co2e / result.area_ha : 0)).toFixed(1)}
            unit="tCO₂e/ha"
            subtitle="Above & below ground pools"
            icon={BarChart3}
            trend={{ direction: "up", text: "Multi-pool calibrated" }}
          />

          <StatCard
            title="Canopy Cover"
            value={typeof result.canopy_cover_pct === "number" ? Number(result.canopy_cover_pct.toFixed(1)) : 0}
            unit="%"
            subtitle={result.mean_canopy_height_m ? `Mean height: ${result.mean_canopy_height_m.toFixed(1)}m` : "Canopy height analyzed"}
            icon={Sparkles}
            variant="ring"
          />

          <StatCard
            title="Confidence Score"
            value={Math.round(result.confidence_score > 1 ? result.confidence_score : result.confidence_score * 100)}
            unit="/100"
            subtitle={result.confidence_label || "IPCC Satellite Standard"}
            icon={ShieldCheck}
            trend={{ direction: "up", text: "Audit Ready" }}
          />
        </div>

        {/* Satellite Map with AOI Polygon */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                Satellite Boundary &amp; Carbon Density Overlay
              </h2>
              <p className="text-xs text-gray-500">
                Multi-spectral 10m Sentinel-2 reflectance with GEDI 3D canopy height calibration
              </p>
            </div>
            <span className="font-mono text-xs bg-green-50 text-green-700 border border-green-200 px-2.5 py-1 rounded-full">
              Area: {result.area_ha?.toLocaleString() ?? "—"} ha
            </span>
          </div>
          <ResultsMap polygon={polygon} />
        </div>

        {/* Gemini 3.8 Flash AI Ecological Audit & Interactive Q&A */}
        <div>
          <AiEcologicalSummary result={result} />
        </div>

        {/* Spaceborne Multi-Sensor Telemetry & Heterogeneous Stratification */}
        <div>
          <SpaceborneTelemetry result={result} />
        </div>

        {/* Detailed Forest Characteristics & Carbon Credits Viability */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          <ForestTable result={result} />
          <CarbonPotential result={result} />
        </div>

        {/* Multi-Year NDVI Historical Trend */}
        <div>
          <NdviChart data={result.ndvi_trend} />
        </div>

        {/* Scientific Methodology Accordion */}
        <div>
          <Methodology />
        </div>

        {/* Bottom Call to Action */}
        <div className="bg-gradient-to-r from-green-900 to-forest text-white rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
          <div className="space-y-2">
            <h3 className="text-xl font-bold">Ready to verify or register this forest tract?</h3>
            <p className="text-sm text-green-100 max-w-xl">
              CanopyAI partners with certified carbon registries and auditors to fast-track your Project Design Document (PDD) submission.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <ExportReportButton result={result} />
            <Button
              className="bg-white text-forest hover:bg-green-50 font-semibold"
              asChild
            >
              <Link href="/pricing">Upgrade for PDD Export</Link>
            </Button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
