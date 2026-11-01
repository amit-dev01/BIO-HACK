"use client";

import React from "react";
import { DollarSign, ExternalLink, ShieldCheck, TrendingUp } from "lucide-react";
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
  let viabilityClass = "bg-green-100 text-green-800 border-green-200";
  if (confidenceScore < 50) {
    viabilityText = "Low";
    viabilityClass = "bg-red-100 text-red-800 border-red-200";
  } else if (confidenceScore <= 70) {
    viabilityText = "Medium";
    viabilityClass = "bg-amber-100 text-amber-800 border-amber-200";
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 border-t-4 border-t-green-500 p-6 flex flex-col justify-between">
      <div>
        {/* Header with Icon & Viability Badge */}
        <div className="flex items-center justify-between pb-6 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2.5 rounded-xl bg-green-50 text-green-700 border border-green-200/60">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-lg tracking-tight">
                Carbon Credit Potential
              </h3>
              <p className="text-xs text-gray-400">
                Annual crediting capacity & revenue pre-feasibility
              </p>
            </div>
          </div>

          {/* Project Viability Badge */}
          <div className="text-right">
            <span className="text-[10px] uppercase font-semibold text-gray-400 block mb-0.5">
              Project Viability
            </span>
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold border ${viabilityClass}`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              {viabilityText}
            </span>
          </div>
        </div>

        {/* Four Key Metrics Rows */}
        <div className="divide-y divide-gray-100 my-4">
          {/* Annual Sequestration */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Annual Sequestration
              </span>
              <p className="text-xs text-gray-400 mt-0.5">
                Expected annual net carbon sink
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold font-mono text-gray-900">
                {annualSeq.toLocaleString()}
              </span>
              <span className="text-xs text-gray-500 font-mono ml-1">
                tCO₂e/yr
              </span>
            </div>
          </div>

          {/* Potential Revenue */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Potential Revenue
              </span>
              <p className="text-xs text-gray-400 mt-0.5">
                Estimated gross carbon credit issuance value
              </p>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold font-mono text-green-700">
                ${revenue.toLocaleString()}
              </span>
              <span className="text-xs text-green-600 font-mono ml-1">/yr</span>
            </div>
          </div>

          {/* Carbon Price Assumption */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Carbon Price Assumption
              </span>
              <p className="text-xs text-gray-400 mt-0.5">
                Voluntary market high-integrity nature credits
              </p>
            </div>
            <div className="text-right">
              <span className="text-base font-semibold font-mono text-gray-600">
                ${price.toFixed(2)}
              </span>
              <span className="text-xs text-gray-400 font-mono ml-1">
                /tCO₂e
              </span>
            </div>
          </div>

          {/* Recommended Standard */}
          <div className="py-4 flex items-center justify-between">
            <div>
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Recommended Standard
              </span>
              <p className="text-xs text-gray-400 mt-0.5">
                Optimal methodology for tropical biomass
              </p>
            </div>
            <div className="text-right">
              <a
                href="https://verra.org"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-green-700 hover:text-green-800 bg-green-50 hover:bg-green-100 px-2.5 py-1 rounded-md border border-green-200 transition-colors"
              >
                <span>{standard}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 leading-relaxed italic">
          This is a pre-feasibility estimate. A full carbon credit verification
          requires on-ground assessment, additionality audits, and validation
          body sign-off.
        </p>
      </div>
    </div>
  );
}

export default CarbonPotential;

