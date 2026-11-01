"use client";

import React, { useState } from "react";
import Navbar from "@/components/layout/Navbar";
import { MapView } from "@/components/analysis/MapView";
import { AnalysisPanel } from "@/components/analysis/AnalysisPanel";
import { AnalysisProgress } from "@/components/analysis/AnalysisProgress";
import { SlidersHorizontal, X } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";

export default function AnalyzePage() {
  const [panelOpen, setPanelOpen] = useState(false);
  const { state } = useAnalysis();

  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col bg-gray-950">
      {/* Fixed Navbar at Top */}
      <div className="h-16 shrink-0 relative z-40">
        <Navbar transparent={false} />
      </div>

      {/* Main Container: MapView filling 100% of remaining height & width */}
      <div className="relative flex-1 w-full h-full overflow-hidden">
        <MapView />

        {/* Toggle Analysis Configuration Panel Button (Top Right) */}
        <div className="absolute top-4 right-4 z-30">
          <button
            type="button"
            onClick={() => setPanelOpen(!panelOpen)}
            className="flex items-center gap-2 px-3.5 py-2.5 bg-white/95 hover:bg-white text-gray-800 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200 text-xs font-bold transition-all hover:scale-105"
          >
            {panelOpen ? (
              <>
                <X className="w-4 h-4 text-gray-500" />
                <span>Close Parameters</span>
              </>
            ) : (
              <>
                <SlidersHorizontal className="w-4 h-4 text-green-700" />
                <span>Sensor Parameters</span>
                {state.polygon && (
                  <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-ping" />
                )}
              </>
            )}
          </button>
        </div>

        {/* Sliding Side Panel for Analysis Parameters & Drone Upload */}
        {panelOpen && (
          <div className="absolute top-16 right-4 bottom-6 w-96 max-w-[calc(100vw-2rem)] z-30 overflow-y-auto rounded-3xl shadow-2xl animate-in slide-in-from-right-4 duration-200">
            <AnalysisPanel />
          </div>
        )}

        {/* Modal Progress Overlay when Analysis is Running */}
        <AnalysisProgress />
      </div>
    </div>
  );
}
