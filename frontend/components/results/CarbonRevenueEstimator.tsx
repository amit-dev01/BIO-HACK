"use client";

import React from "react";
import { AnalysisResult } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export interface CarbonRevenueEstimatorProps {
  result: AnalysisResult;
}

export function CarbonRevenueEstimator({ result }: CarbonRevenueEstimatorProps) {
  return (
    <Card className="border-forest/30 bg-forest-50/30">
      <CardHeader>
        <CardTitle className="text-base text-forest">Carbon Credit Revenue Estimate</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-slate">Standard Assumed:</span>
          <span className="font-semibold text-charcoal">{result.recommended_standard}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate">Price Assumption:</span>
          <span className="font-mono">${result.credit_price_assumption_usd} / tCO2e</span>
        </div>
        <div className="flex justify-between items-baseline pt-2 border-t border-forest/20">
          <span className="text-sm font-semibold text-charcoal">Est. Annual Revenue:</span>
          <span className="text-2xl font-bold font-mono text-forest">
            ${result.credit_revenue_estimate_usd.toLocaleString()}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}

export default CarbonRevenueEstimator;

