"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";

export interface MetricsGridProps {
  result: AnalysisResult;
}

export function MetricsGrid({ result }: MetricsGridProps) {
  const items = [
    { label: "Total Area", value: `${result.area_ha.toLocaleString()} ha` },
    { label: "Canopy Cover", value: `${result.canopy_cover_pct}%` },
    { label: "Mean Canopy Height", value: `${result.mean_canopy_height_m} m` },
    { label: "Total CO2e", value: `${result.total_co2e.toLocaleString()} tCO2e` },
    { label: "Annual Sequestration", value: `${result.annual_sequestration_tco2e.toLocaleString()} tCO2e/yr` },
    { label: "Confidence Score", value: `${result.confidence_score}%` },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {items.map((item, idx) => (
        <Card key={idx}>
          <CardContent className="p-4">
            <span className="text-xs uppercase text-slate font-medium">{item.label}</span>
            <div className="text-xl font-bold font-mono text-forest mt-1">{item.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default MetricsGrid;

