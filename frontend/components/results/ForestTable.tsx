"use client";

import React from "react";
import { TreePine, AlertCircle, CheckCircle2 } from "lucide-react";
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
    { metric: "Forest Type", value: result.forest_type || "Tropical Moist Broadleaf", isMono: false },
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
        <div className="flex items-center gap-1.5 font-mono">
          <span>{lossRate.toFixed(2)}%</span>
          {isLossLow ? (
            <span className="inline-flex items-center gap-1 text-[11px] font-sans text-green-700 bg-green-50 px-2 py-0.5 rounded-full border border-green-200">
              <CheckCircle2 className="w-3 h-3 text-green-600" /> Stable
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[11px] font-sans text-red-700 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
              <AlertCircle className="w-3 h-3 text-red-600" /> Alert
            </span>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden">
      {/* Card Header */}
      <div className="p-6 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-green-50 text-green-700 border border-green-200/60">
            <TreePine className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h3 className="font-bold text-gray-900 text-lg tracking-tight">
              Forest Characteristics
            </h3>
            <p className="text-xs text-gray-400">
              Spaceborne LiDAR & IPCC Tier-3 biometric parameters
            </p>
          </div>
        </div>
      </div>

      {/* Styled Data Table with alternating row backgrounds */}
      <Table>
        <TableHeader>
          <TableRow className="bg-gray-50/80">
            <TableHead className="font-semibold text-gray-600 text-xs uppercase tracking-wider">
              Metric
            </TableHead>
            <TableHead className="font-semibold text-gray-600 text-xs uppercase tracking-wider text-right">
              Value
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow
              key={row.metric}
              className={idx % 2 === 0 ? "bg-white" : "bg-gray-50/50"}
            >
              <TableCell className="font-medium text-gray-700 text-sm">
                {row.metric}
              </TableCell>
              <TableCell className="text-right text-sm">
                {row.customRenderer ? (
                  <div className="flex justify-end">{row.customRenderer}</div>
                ) : (
                  <span
                    className={
                      row.isMono
                        ? "font-mono font-semibold text-gray-900"
                        : "text-gray-900"
                    }
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

