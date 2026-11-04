"use client";

import React from "react";
import { useAnalysis } from "@/context/AnalysisContext";

export function SatelliteScanOverlay() {
  const { state } = useAnalysis();

  // Vanishes immediately when user draws a polygon or analysis runs
  if (state.polygon || state.analysisStatus !== "idle") {
    return null;
  }

  return (
    <div className="absolute inset-0 pointer-events-none z-20 overflow-hidden select-none transition-opacity duration-300">
      {/* 1. Thin Horizontal Scanning Line (1px height) with Green Glow and Phosphor Trail */}
      <div className="absolute left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-[#4CAF50] to-transparent shadow-[0_0_20px_#4CAF50,0_0_60px_rgba(76,175,80,0.4)] animate-radar-sweep">
        {/* Fading 30px Phosphor Trail */}
        <div className="absolute bottom-full left-0 w-full h-8 bg-gradient-to-t from-green-500/15 via-green-500/5 to-transparent" />
      </div>

      {/* 2. Grid Overlay: Faint 100px Grid Pulsing 3% to 6% Opacity */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:100px_100px] animate-grid-breathe" />

      {/* 3. Corner Brackets (Targeting Reticles) Rotating ±5 deg */}
      <div className="absolute top-6 left-6 w-10 h-10 border-t-2 border-l-2 border-green-500/40 animate-reticle-turn" />
      <div className="absolute top-6 right-6 w-10 h-10 border-t-2 border-r-2 border-green-500/40 animate-reticle-turn" />
      <div className="absolute bottom-6 left-6 w-10 h-10 border-b-2 border-l-2 border-green-500/40 animate-reticle-turn" />
      <div className="absolute bottom-6 right-6 w-10 h-10 border-b-2 border-r-2 border-green-500/40 animate-reticle-turn" />

      {/* 4. Transient Sensor Collection Data Dots */}
      <div className="absolute top-1/4 left-1/5 w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
      <div className="absolute top-3/5 left-3/4 w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse delay-500" />
      <div className="absolute top-1/2 left-1/3 w-1.5 h-1.5 rounded-full bg-lime-300 animate-pulse delay-1000" />
      <div className="absolute top-4/5 left-1/2 w-1.5 h-1.5 rounded-full bg-teal-400 animate-ping delay-700" />
    </div>
  );
}

export default SatelliteScanOverlay;

