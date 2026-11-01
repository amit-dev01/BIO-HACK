"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export interface BiomassBreakdownProps {
  result: AnalysisResult;
}

export function BiomassBreakdown({ result }: BiomassBreakdownProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base text-forest">Biomass & Carbon Distribution</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-slate">Above-Ground Biomass (AGB):</span>
          <span className="font-mono font-semibold">{result.agb_t_per_ha} t/ha</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate">Below-Ground Biomass (BGB):</span>
          <span className="font-mono font-semibold">{result.bgb_t_per_ha} t/ha</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate">Total Biomass Density:</span>
          <span className="font-mono font-semibold">{result.total_biomass_t_per_ha} t/ha</span>
        </div>
        <div className="flex justify-between text-sm border-t pt-2">
          <span className="text-slate">Carbon Fraction:</span>
          <span className="font-mono font-semibold">{result.carbon_fraction * 100}%</span>
        </div>
        <div className="flex justify-between text-sm font-bold text-forest">
          <span>Carbon Density:</span>
          <span className="font-mono">{result.carbon_t_per_ha} t C/ha</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default BiomassBreakdown;

