"use client";

import React, { useState } from "react";
import {
  useAnalysis } from "@/context/AnalysisContext";
import { DroneUploader } from "./DroneUploader";
import { Checkbox } from "@/components/ui/checkbox";
import {
  TreePine,
  Leaf,
  MapPin,
  X,
  AlertTriangle,
  Satellite,
  Radio,
  Globe,
  Info,
  ChevronDown,
  Layers,
  Sparkles,
} from "lucide-react";

export function AnalysisPanel() {
  const { state, dispatch, runAnalysis } = useAnalysis();

  const [droneOpen, setDroneOpen] = useState(false);
  const [dataSources, setDataSources] = useState({
    sentinel: true,
    gedi: true,
    dynamicWorld: true,
  });
  const [analysisType, setAnalysisType] = useState<"quick" | "detailed">("quick");
  const [droneFile, setDroneFile] = useState<File | null>(null);

  const areaHa = state.areaHa;
  const hasPolygon = !!state.polygon && areaHa !== null;
  const isTooSmall = hasPolygon && areaHa < 10;
  const isTooLarge = hasPolygon && areaHa > 100000;
  const isValidArea = hasPolygon && !isTooSmall && !isTooLarge;

  // Calculate polygon center coordinates
  let centerCoords = "-3.05°, -52.20°";
  let bboxText = "N/A";
  if (state.polygon?.geometry?.coordinates?.[0]) {
    const ring = state.polygon.geometry.coordinates[0];
    let sumLng = 0;
    let sumLat = 0;
    let minLng = Infinity,
      maxLng = -Infinity,
      minLat = Infinity,
      maxLat = -Infinity;
    for (const pt of ring) {
      sumLng += pt[0];
      sumLat += pt[1];
      minLng = Math.min(minLng, pt[0]);
      maxLng = Math.max(maxLng, pt[0]);
      minLat = Math.min(minLat, pt[1]);
      maxLat = Math.max(maxLat, pt[1]);
    }
    const cLng = (sumLng / ring.length).toFixed(2);
    const cLat = (sumLat / ring.length).toFixed(2);
    centerCoords = `${cLat}°, ${cLng}°`;
    bboxText = `[${minLat.toFixed(2)}, ${minLng.toFixed(2)}] → [${maxLat.toFixed(2)}, ${maxLng.toFixed(2)}]`;
  }

  const handleDroneFile = (file: File | null) => {
    setDroneFile(file);
    dispatch({
      type: "SET_CONFIG",
      payload: { drone_image: file },
    });
    if (!file && analysisType === "detailed") {
      setAnalysisType("quick");
    }
  };

  const handleRun = () => {
    if (!isValidArea) return;
    runAnalysis();
  };

  return (
    <div className="w-full h-full flex flex-col bg-white/95 backdrop-blur-xl border border-gray-100 overflow-hidden rounded-3xl shadow-2xl">
      {/* Header */}
      <div className="p-6 border-b border-gray-200/80 bg-white sticky top-0 z-10 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-green-50 text-green-700 border border-green-200/60">
            <Leaf className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 tracking-tight">
              Analysis Configuration
            </h2>
            <p className="text-xs text-gray-500">
              Multi-sensor satellite biomass & carbon setup
            </p>
          </div>
        </div>
      </div>

      {/* Scrollable Configuration Sections */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* Section 1 — Selected Area */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-700 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-green-600" />
              Selected Area
            </h3>
            {hasPolygon && (
              <button
                type="button"
                onClick={() => dispatch({ type: "CLEAR_POLYGON" })}
                className="text-xs font-medium text-red-600 hover:text-red-700 flex items-center gap-1 hover:underline"
              >
                <X className="w-3.5 h-3.5" />
                Clear selection
              </button>
            )}
          </div>

          {!hasPolygon ? (
            /* Empty State */
            <div className="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center bg-gray-50/50">
              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto text-gray-400 mb-3">
                <MapPin className="w-6 h-6" />
              </div>
              <p className="text-sm font-medium text-gray-700">
                No area selected
              </p>
              <p className="text-xs text-gray-500 mt-1 max-w-xs mx-auto">
                Draw a polygon on the map or click the &ldquo;Load Demo Forest Plot&rdquo; button to begin your analysis.
              </p>
            </div>
          ) : (
            /* Selected Polygon Card */
            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm space-y-4 animate-in fade-in">
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-xs font-semibold uppercase text-gray-400 block mb-1">
                    Total Forest Area
                  </span>
                  <div className="text-4xl font-bold font-mono text-green-700">
                    {areaHa?.toLocaleString()}{" "}
                    <span className="text-xl font-medium text-green-600">ha</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-semibold uppercase text-gray-400 block mb-1">
                    Center Coordinates
                  </span>
                  <span className="text-sm font-mono text-gray-600 font-semibold bg-gray-100 px-2.5 py-1 rounded-md">
                    {centerCoords}
                  </span>
                </div>
              </div>

              {/* Bounding Box Info */}
              <div className="text-xs text-gray-500 pt-2 border-t border-gray-100 flex items-center justify-between">
                <span className="text-gray-400">Bounding Box:</span>
                <span className="font-mono text-gray-600 truncate max-w-[200px]">
                  {bboxText}
                </span>
              </div>

              {/* Forest Type Display */}
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <TreePine className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="text-xs font-bold text-gray-700">Forest Type:</span>
                </div>
                <span className="text-xs font-semibold text-emerald-800 bg-white/80 px-2.5 py-0.5 rounded-full border border-emerald-200 truncate max-w-[180px]">
                  {state.polygon?.properties?.forest_type || "Tropical Wet Evergreen Rainforest"}
                </span>
              </div>

              {/* Validation Warnings */}
              {isTooSmall && (
                <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
                  <span>Area too small (minimum 10 ha)</span>
                </div>
              )}

              {isTooLarge && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 text-red-600" />
                  <span>Area too large (maximum 100,000 ha)</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section 2 — Data Sources */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-700 flex items-center gap-2">
              <Layers className="w-4 h-4 text-green-600" />
              Data Sources
            </h3>
            <span
              className="text-gray-400 hover:text-gray-600 cursor-pointer"
              title="Remote sensing instruments fused for Tier-3 carbon estimation"
            >
              <Info className="w-4 h-4" />
            </span>
          </div>

          <div className="space-y-3">
            {/* Sentinel-2 */}
            <div className="p-4 rounded-xl border border-gray-200 bg-white hover:border-gray-300 transition-colors">
              <div className="flex items-start gap-3">
                <Checkbox
                  id="source-sentinel"
                  checked={dataSources.sentinel}
                  onCheckedChange={(checked) =>
                    setDataSources((prev) => ({ ...prev, sentinel: checked }))
                  }
                  className="mt-0.5"
                />
                <div className="flex-1">
                  <label
                    htmlFor="source-sentinel"
                    className="text-sm font-semibold text-gray-900 cursor-pointer flex items-center gap-2"
                  >
                    <Satellite className="w-4 h-4 text-blue-600" />
                    Sentinel-2 (Optical, 10m resolution)
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    Multi-spectral surface reflectance & vegetation index tracking
                  </p>
                </div>
              </div>
            </div>

            {/* NASA GEDI */}
            <div className="p-4 rounded-xl border border-gray-200 bg-white hover:border-gray-300 transition-colors">
              <div className="flex items-start gap-3">
                <Checkbox
                  id="source-gedi"
                  checked={dataSources.gedi}
                  onCheckedChange={(checked) =>
                    setDataSources((prev) => ({ ...prev, gedi: checked }))
                  }
                  className="mt-0.5"
                />
                <div className="flex-1">
                  <label
                    htmlFor="source-gedi"
                    className="text-sm font-semibold text-gray-900 cursor-pointer flex items-center gap-2"
                  >
                    <Radio className="w-4 h-4 text-emerald-600" />
                    NASA GEDI (LiDAR, 25m resolution)
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    Spaceborne LiDAR full-waveform canopy height & vertical profile metrics
                  </p>
                </div>
              </div>
            </div>

            {/* Dynamic World */}
            <div className="p-4 rounded-xl border border-gray-200 bg-white hover:border-gray-300 transition-colors">
              <div className="flex items-start gap-3">
                <Checkbox
                  id="source-dw"
                  checked={dataSources.dynamicWorld}
                  onCheckedChange={(checked) =>
                    setDataSources((prev) => ({ ...prev, dynamicWorld: checked }))
                  }
                  className="mt-0.5"
                />
                <div className="flex-1">
                  <label
                    htmlFor="source-dw"
                    className="text-sm font-semibold text-gray-900 cursor-pointer flex items-center gap-2"
                  >
                    <Globe className="w-4 h-4 text-purple-600" />
                    Dynamic World (Land Cover, 10m)
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    Near real-time 10m global land use and canopy cover classification
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section 3 — Upload Drone Image (Collapsible, Optional) */}
        <div className="border border-gray-200 rounded-2xl overflow-hidden bg-white">
          <button
            type="button"
            onClick={() => setDroneOpen(!droneOpen)}
            className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-gray-900">
                  Upload Drone Image
                </h3>
                <span className="text-[10px] font-semibold uppercase bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  Optional
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">
                Sub-meter RGB/multispectral orthomosaics for millimeter biomass accuracy
              </p>
            </div>
            <ChevronDown
              className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                droneOpen ? "rotate-180" : ""
              }`}
            />
          </button>

          {droneOpen && (
            <div className="p-4 pt-0 border-t border-gray-100">
              <DroneUploader
                onFileSelect={handleDroneFile}
                selectedFile={droneFile}
              />
            </div>
          )}
        </div>

        {/* Section 4 — Analysis Type (Radio Buttons) */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-700 mb-3">
            Analysis Type
          </h3>
          <div className="grid grid-cols-1 gap-3">
            {/* Quick Estimate */}
            <label
              className={`p-4 rounded-xl border cursor-pointer flex items-start gap-3 transition-all ${
                analysisType === "quick"
                  ? "border-green-600 bg-green-50/40 shadow-sm"
                  : "border-gray-200 hover:border-gray-300 bg-white"
              }`}
            >
              <input
                type="radio"
                name="analysisType"
                value="quick"
                checked={analysisType === "quick"}
                onChange={() => setAnalysisType("quick")}
                className="mt-1 text-green-600 focus:ring-green-600"
              />
              <div>
                <span className="text-sm font-semibold text-gray-900 block">
                  Quick Estimate
                </span>
                <span className="text-xs text-gray-500 mt-0.5 block">
                  Satellite data only, ~30 seconds
                </span>
              </div>
            </label>

            {/* Detailed Assessment */}
            <label
              className={`p-4 rounded-xl border flex items-start gap-3 transition-all ${
                !droneFile
                  ? "opacity-50 cursor-not-allowed bg-gray-50 border-gray-200"
                  : analysisType === "detailed"
                  ? "border-green-600 bg-green-50/40 shadow-sm cursor-pointer"
                  : "border-gray-200 hover:border-gray-300 bg-white cursor-pointer"
              }`}
            >
              <input
                type="radio"
                name="analysisType"
                value="detailed"
                disabled={!droneFile}
                checked={analysisType === "detailed"}
                onChange={() => droneFile && setAnalysisType("detailed")}
                className="mt-1 text-green-600 focus:ring-green-600"
              />
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-gray-900">
                    Detailed Assessment
                  </span>
                  {!droneFile && (
                    <span className="text-[10px] bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded">
                      Requires drone image
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-500 mt-0.5 block">
                  Satellite + drone fusion, ~2 minutes
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Sticky Bottom: Run Analysis Button */}
      <div className="p-6 border-t border-gray-200 bg-white sticky bottom-0 z-10 shadow-lg">
        <button
          type="button"
          onClick={handleRun}
          disabled={!isValidArea || state.analysisStatus === "loading"}
          className={`w-full py-4 px-6 rounded-xl font-bold text-base transition-all duration-200 flex items-center justify-center gap-2 shadow-lg ${
            isValidArea && state.analysisStatus !== "loading"
              ? "bg-green-600 hover:bg-green-700 text-white shadow-green-900/30 hover:shadow-green-900/50 hover:-translate-y-0.5 animate-pulse"
              : "bg-gray-200 text-gray-400 cursor-not-allowed"
          }`}
        >
          <span>🚀 Run Carbon Analysis</span>
        </button>

        {!hasPolygon && (
          <p className="text-[11px] text-gray-400 text-center mt-2">
            Draw a forest boundary to enable analysis
          </p>
        )}
      </div>
    </div>
  );
}

export default AnalysisPanel;

