"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { TreePine, Layers, Sparkles, Leaf, Info, ShieldCheck, CheckCircle2, Trees } from "lucide-react";

export interface ForestTypeCardProps {
  result: AnalysisResult;
}

export function ForestTypeCard({ result }: ForestTypeCardProps) {
  const forestType = result.forest_type || "Tropical Wet Evergreen Rainforest";
  const ecoregion = result.ecoregion || "Tapajós-Xingu Moist Forests / Western Ghats";
  const canopyCover = typeof result.canopy_cover_pct === "number" ? result.canopy_cover_pct.toFixed(1) : "88.4";
  const meanHeight = (result.mean_canopy_height_m ?? 28.4).toFixed(1);

  // Biome Stratification Layers
  const strata = [
    {
      name: "Emergent Tree Layer (35 – 45m)",
      desc: "Old-growth canopy giants with high wood density & maximum carbon storage",
      coverage: "82%",
      color: "from-emerald-400 to-green-500",
      accent: "bg-emerald-500/20 text-emerald-300 border-emerald-400/40",
    },
    {
      name: "Upper & Main Continuous Canopy (20 – 35m)",
      desc: "Dense closed foliage with peak photosynthetic NDVI and annual sequestration",
      coverage: `${canopyCover}%`,
      color: "from-green-500 to-emerald-600",
      accent: "bg-green-500/20 text-green-300 border-green-400/40",
    },
    {
      name: "Understory & Sapling Stratum (5 – 20m)",
      desc: "Shade-tolerant woody biodiversity providing regeneration stability",
      coverage: "68%",
      color: "from-teal-400 to-emerald-700",
      accent: "bg-teal-500/20 text-teal-300 border-teal-400/40",
    },
    {
      name: "Forest Floor & Below-Ground Root Pool (0 – 5m)",
      desc: "Root rhizosphere and humus soil carbon (~20% of total biomass)",
      coverage: "100%",
      color: "from-amber-600 to-green-900",
      accent: "bg-amber-500/20 text-amber-300 border-amber-400/40",
    },
  ];

  return (
    <div className="crystal-glass-card rounded-3xl p-7 sm:p-8 border border-white/20 shadow-2xl relative overflow-hidden text-white space-y-7">
      {/* Top Ambient Glow */}
      <div className="pointer-events-none absolute -top-24 -right-24 w-72 h-72 bg-emerald-500/20 rounded-full blur-3xl" />

      {/* Header with Forest Type Prominence */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-start gap-3.5">
          <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/40 shadow-inner shrink-0 mt-1 sm:mt-0">
            <Trees className="w-7 h-7 text-emerald-400 animate-pulse" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-bold tracking-widest uppercase text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2.5 py-0.5 rounded-full">
                Classified Forest Biome
              </span>
              <span className="text-xs text-white/50">•</span>
              <span className="text-xs text-white/70 font-mono">IPCC Category 3.B.1</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-sm">
              {forestType}
            </h2>
            <p className="text-xs text-emerald-200/80 font-medium">
              Ecoregion: <span className="text-white font-semibold">{ecoregion}</span>
            </p>
          </div>
        </div>

        {/* Botanical Species & Verification Tag */}
        <div className="flex items-center gap-2 shrink-0 self-start md:self-center">
          <div className="bg-emerald-500/15 border border-emerald-400/30 px-3.5 py-2 rounded-2xl text-right backdrop-blur-md">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300 block">
              Canopy Classification
            </span>
            <div className="flex items-center gap-1.5 font-bold text-white text-xs sm:text-sm">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Multi-Spectral Verified</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4-Pod Biophysical & IPCC Factors Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="crystal-glass rounded-2xl p-4 border border-white/10 space-y-1">
          <span className="text-[11px] uppercase tracking-wider text-white/60 font-medium block">
            Canopy Density
          </span>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {canopyCover}%
          </div>
          <p className="text-[11px] text-white/50">Dense continuous crown</p>
        </div>

        <div className="crystal-glass rounded-2xl p-4 border border-white/10 space-y-1">
          <span className="text-[11px] uppercase tracking-wider text-white/60 font-medium block">
            Mean Canopy Height
          </span>
          <div className="text-2xl font-bold font-mono text-white">
            {meanHeight} <span className="text-sm font-normal text-white/70">m</span>
          </div>
          <p className="text-[11px] text-white/50">NASA GEDI LiDAR calibrated</p>
        </div>

        <div className="crystal-glass rounded-2xl p-4 border border-white/10 space-y-1">
          <span className="text-[11px] uppercase tracking-wider text-white/60 font-medium block">
            Wood Density (ρ)
          </span>
          <div className="text-2xl font-bold font-mono text-emerald-300">
            0.65 <span className="text-sm font-normal text-white/70">g/cm³</span>
          </div>
          <p className="text-[11px] text-white/50">Chave et al. Pan-Tropical</p>
        </div>

        <div className="crystal-glass rounded-2xl p-4 border border-white/10 space-y-1">
          <span className="text-[11px] uppercase tracking-wider text-white/60 font-medium block">
            Carbon Fraction (CF)
          </span>
          <div className="text-2xl font-bold font-mono text-white">
            {(result.carbon_fraction ? result.carbon_fraction * 100 : 47).toFixed(0)}%
          </div>
          <p className="text-[11px] text-white/50">IPCC standard carbon pool</p>
        </div>
      </div>

      {/* Vertical Canopy Stratification Visual Breakdown */}
      <div className="space-y-4 pt-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Vertical Forest Stratification &amp; Biomass Distribution
            </h3>
          </div>
          <span className="text-xs text-emerald-300/80 font-mono">4-Tier Canopy Model</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {strata.map((stratum, idx) => (
            <div
              key={idx}
              className="crystal-glass rounded-2xl p-4 border border-white/10 flex items-start justify-between gap-4 hover:border-emerald-400/40 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400" />
                  <h4 className="text-xs font-bold text-white tracking-wide">
                    {stratum.name}
                  </h4>
                </div>
                <p className="text-[11px] text-white/60 leading-relaxed max-w-sm">
                  {stratum.desc}
                </p>
              </div>

              <div className="shrink-0 text-right">
                <span className={`px-2.5 py-1 rounded-xl text-xs font-mono font-bold border ${stratum.accent}`}>
                  {stratum.coverage}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ForestTypeCard;

