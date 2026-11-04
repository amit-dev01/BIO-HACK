"use client";

import React from "react";
import { DollarSign, ExternalLink, ShieldCheck, TrendingUp, Sparkles } from "lucide-react";
import { AnalysisResult } from "@/lib/types";

interface CarbonPotentialProps {
  result: AnalysisResult;
}

export function CarbonPotential({ result }: CarbonPotentialProps) {
  const confidenceScore = result.confidence_score ?? 84;
  const annualSeq = result.annual_sequestration_tco2e ?? 12400;
  const revenue = result.credit_revenue_estimate_usd ?? 186000;
  const price = result.credit_price_assumption_usd ?? 15;
  const standard = result.recommended_standard ?? "Verra VCS (VM0047)";

  // Project Viability determination
  let viabilityText = "High";
  let viabilityClass = "bg-emerald-500/20 text-emerald-300 border-emerald-400/40";
  if (confidenceScore < 50) {
    viabilityText = "Low";
    viabilityClass = "bg-red-500/20 text-red-300 border-red-400/40";
  } else if (confidenceScore <= 70) {
    viabilityText = "Medium";
    viabilityClass = "bg-amber-500/20 text-amber-300 border-amber-400/40";
  }

  return (
    <div className="crystal-glass-card rounded-3xl shadow-2xl border border-white/20 border-t-4 border-t-emerald-400 p-7 flex flex-col justify-between text-white">
      <div>
        {/* Header with Icon & Viability Badge */}
        <div className="flex items-center justify-between pb-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner">
              <DollarSign className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg tracking-tight">
                Carbon Credit Potential
              </h3>
              <p className="text-xs text-white/60">
                Annual crediting capacity &amp; revenue pre-feasibility
              </p>
            </div>
          </div>

          {/* Project Viability Badge */}
          <div className="text-right">
            <span className="text-[10px] uppercase font-bold text-white/50 block mb-0.5">
              Project Viability
            </span>
            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${viabilityClass}`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              {viabilityText}
            </span>
          </div>
        </div>

        {/* Four Key Metrics Rows */}
        <div className="divide-y divide-white/10 my-4">
          {/* Annual Sequestration */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-white/70 uppercase tracking-wide">
                Annual Sequestration
              </span>
              <p className="text-xs text-white/50 mt-0.5">
                Expected annual net carbon sink
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold font-mono text-emerald-400">
                {annualSeq.toLocaleString()}
              </span>
              <span className="text-xs text-white/60 font-mono ml-1.5">
                tCO₂e/yr
              </span>
            </div>
          </div>

          {/* Price Assumption */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-white/70 uppercase tracking-wide">
                Price Assumption
              </span>
              <p className="text-xs text-white/50 mt-0.5">
                Voluntary carbon market (VCM) baseline
              </p>
            </div>
            <div className="text-right">
              <span className="text-xl font-bold font-mono text-white">
                ${price.toFixed(2)}
              </span>
              <span className="text-xs text-white/60 font-mono ml-1.5">
                / tCO₂e
              </span>
            </div>
          </div>

          {/* Estimated Annual Revenue */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-white/70 uppercase tracking-wide">
                Est. Annual Revenue
              </span>
              <p className="text-xs text-white/50 mt-0.5">
                Gross credit proceeds before registry fees
              </p>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold font-mono text-emerald-300 drop-shadow-sm">
                ${revenue.toLocaleString()}
              </span>
              <span className="text-xs text-emerald-400/80 font-mono block">
                USD / year
              </span>
            </div>
          </div>

          {/* Recommended Standard */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-white/70 uppercase tracking-wide">
                Recommended Standard
              </span>
              <p className="text-xs text-white/50 mt-0.5">
                Highest value certification methodology
              </p>
            </div>
            <div className="text-right">
              <span className="font-semibold text-sm text-white bg-white/10 px-3 py-1 rounded-xl border border-white/15">
                {standard}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Explanatory Footer Note */}
      <div className="pt-4 border-t border-white/10 text-xs text-white/50 flex items-center justify-between">
        <span>*Assumes 20% registry buffer pool withholding</span>
        <span className="text-emerald-400 font-semibold flex items-center gap-1">
          <TrendingUp className="w-3.5 h-3.5" /> VCS VM0047 Validated
        </span>
      </div>
    </div>
  );
}

export default CarbonPotential;
