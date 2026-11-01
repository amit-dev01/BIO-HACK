"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { TreePine, Calendar, MapPin, ShieldCheck } from "lucide-react";

export interface ResultsHeaderProps {
  result: AnalysisResult;
}

export function ResultsHeader({ result }: ResultsHeaderProps) {
  const dateFormatted = new Date(result.timestamp || Date.now()).toLocaleDateString(
    undefined,
    {
      month: "long",
      day: "numeric",
      year: "numeric",
    }
  );

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
      <div className="space-y-2">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="p-2 rounded-xl bg-green-50 text-green-700">
            <TreePine className="w-6 h-6 text-green-700" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
              {result.polygon?.properties?.name || "Forest Carbon Intelligence Report"}
            </h1>
            <p className="text-xs text-gray-500 font-mono">
              Analysis ID: {result.analysis_id}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-600 flex-wrap pt-1">
          <span className="flex items-center gap-1.5 font-medium">
            <MapPin className="w-3.5 h-3.5 text-green-600" />
            {result.ecoregion}
          </span>
          <span>•</span>
          <span className="text-gray-500">{result.forest_type}</span>
          <span>•</span>
          <span className="flex items-center gap-1.5 text-gray-500">
            <Calendar className="w-3.5 h-3.5 text-gray-400" />
            {dateFormatted}
          </span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
        <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-2 text-right">
          <span className="text-[10px] font-bold uppercase tracking-wider text-green-700 block">
            Verification Grade
          </span>
          <div className="flex items-center gap-1.5 font-bold text-green-900 text-sm font-mono">
            <ShieldCheck className="w-4 h-4 text-green-600" />
            <span>{result.confidence_label || "Tier 3 IPCC"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultsHeader;
