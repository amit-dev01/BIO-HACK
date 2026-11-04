"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { TreePine, Calendar, MapPin, ShieldCheck, Sparkles, Trees } from "lucide-react";

export interface ResultsHeaderProps {
  result: AnalysisResult;
}

export function ResultsHeader({ result }: ResultsHeaderProps) {
  const dateFormatted = new Date(result.timestamp || Date.now()).toLocaleDateString(
    "en-US",
    {
      month: "long",
      day: "numeric",
      year: "numeric",
    }
  );

  const forestType = result.forest_type || "Tropical Wet Evergreen Rainforest";

  return (
    <div className="crystal-glass-card rounded-3xl p-7 border border-white/20 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden text-white">
      {/* Specular top sheen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      <div className="space-y-3">
        <div className="flex items-center gap-3.5 flex-wrap">
          <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner">
            <Trees className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight drop-shadow-sm">
              {result.polygon?.properties?.name || "Forest Carbon Intelligence Report"}
            </h1>
            <p className="text-xs text-white/50 font-mono mt-0.5">
              Analysis ID: {result.analysis_id}
            </p>
          </div>
        </div>

        {/* Prominent Forest Type & Geographic Metadata Badges */}
        <div className="flex items-center gap-3 text-xs flex-wrap pt-1">
          {/* Prominent Glowing Forest Type Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-2xl bg-emerald-500/25 text-emerald-200 border border-emerald-400/40 font-bold shadow-lg shadow-emerald-950/40 backdrop-blur-md">
            <TreePine className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="text-emerald-300 font-medium">Forest Type:</span>
            <span className="text-white font-extrabold tracking-wide">{forestType}</span>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-2xl bg-white/10 text-white/80 border border-white/15 font-medium backdrop-blur-md">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <span>{result.ecoregion || "Global Biosphere"}</span>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-2xl bg-white/10 text-white/70 border border-white/15 font-medium backdrop-blur-md">
            <Calendar className="w-3.5 h-3.5 text-white/50" />
            <span>{dateFormatted}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0">
        <div className="bg-emerald-500/15 border border-emerald-400/30 rounded-2xl px-5 py-3 text-right backdrop-blur-md">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300 block mb-0.5">
            Verification Grade
          </span>
          <div className="flex items-center gap-1.5 font-bold text-white text-sm font-mono justify-end">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>{result.confidence_label || "Tier 3 IPCC Standard"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsHeader;
