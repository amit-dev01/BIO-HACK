"use client";

import React from "react";
import { TreePine, AlertCircle, CheckCircle2, Trees, Sparkles } from "lucide-react";
import { AnalysisResult } from "@/lib/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ForestTableProps {
  result: AnalysisResult;
}

export function ForestTable({ result }: ForestTableProps) {
  const lossRate = result.tree_cover_loss_pct_5yr ?? 0.42;
  const isLossLow = lossRate < 1.0;

  const rows = [
    {
      metric: "Forest Type",
      value: result.forest_type || "Tropical Wet Evergreen Rainforest",
      isMono: false,
      customRenderer: (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-500/25 text-emerald-300 border border-emerald-400/40 text-xs font-bold shadow-xs">
          <TreePine className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span>{result.forest_type || "Tropical Wet Evergreen Rainforest"}</span>
        </span>
      ),
    },
    { metric: "Ecoregion", value: result.ecoregion || "Tapajós-Xingu Moist Forests", isMono: false },
    {
      metric: "Mean Canopy Height",
      value: `${(result.mean_canopy_height_m ?? 28.4).toFixed(1)} m`,
      isMono: true,
    },
    {
      metric: "Above-Ground Biomass",
      value: `${(result.agb_t_per_ha ?? 265.4).toFixed(1)} t/ha`,
      isMono: true,
    },
    {
      metric: "Below-Ground Biomass",
      value: `${(result.bgb_t_per_ha ?? 53.1).toFixed(1)} t/ha`,
      isMono: true,
    },
    {
      metric: "Total Biomass",
      value: `${(result.total_biomass_t_per_ha ?? 318.5).toFixed(1)} t/ha`,
      isMono: true,
    },
    {
      metric: "Carbon Fraction",
      value: `${result.carbon_fraction ?? 0.47} (IPCC default)`,
      isMono: true,
    },
    {
      metric: "Total Area",
      value: `${(result.area_ha ?? 500).toLocaleString()} ha`,
      isMono: true,
    },
    {
      metric: "Tree Cover Loss (5yr)",
      value: `${lossRate.toFixed(2)}%`,
      isMono: true,
      customRenderer: (
        <div className="flex items-center gap-2 font-mono">
          <span className="text-white font-bold">{lossRate.toFixed(2)}%</span>
          {isLossLow ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-sans text-emerald-300 bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-400/30">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Stable
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-sans text-red-300 bg-red-500/20 px-2 py-0.5 rounded-full border border-red-400/30">
              <AlertCircle className="w-3 h-3 text-red-400" /> Alert
            </span>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="crystal-glass-card rounded-3xl shadow-2xl border border-white/20 overflow-hidden text-white">
      {/* Card Header */}
      <div className="p-6 sm:p-7 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner">
            <Trees className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-bold text-white text-lg tracking-tight">
              Forest Biometric Characteristics
            </h3>
            <p className="text-xs text-white/60">
              Spaceborne LiDAR &amp; IPCC Tier-3 biometric parameters
            </p>
          </div>
        </div>
      </div>

      {/* Styled Data Table with alternating row backgrounds */}
      <Table>
        <TableHeader>
          <TableRow className="border-b border-white/10 hover:bg-transparent">
            <TableHead className="font-bold text-emerald-300 text-xs uppercase tracking-wider py-3.5 pl-6">
              Biometric Metric
            </TableHead>
            <TableHead className="font-bold text-emerald-300 text-xs uppercase tracking-wider py-3.5 pr-6 text-right">
              Calculated Value
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, index) => (
            <TableRow
              key={index}
              className={`border-b border-white/5 transition-colors ${
                index % 2 === 0 ? "bg-white/[0.02]" : "bg-transparent"
              } hover:bg-white/[0.06]`}
            >
              <TableCell className="font-medium text-white/90 text-sm py-3.5 pl-6">
                {row.metric}
              </TableCell>
              <TableCell className="text-right py-3.5 pr-6">
                {row.customRenderer ? (
                  <div className="inline-block">{row.customRenderer}</div>
                ) : (
                  <span
                    className={`text-sm text-white ${
                      row.isMono ? "font-mono font-semibold" : ""
                    }`}
                  >
                    {row.value}
                  </span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export default ForestTable;
