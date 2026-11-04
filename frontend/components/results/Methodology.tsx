"use client";

import React, { useState, useEffect } from "react";
import {
  ChevronDown,
  Info,
  CheckCircle2,
  FileCheck2,
  Cpu,
  BarChart4,
  TreePine,
  ShieldAlert,
  ArrowRight,
} from "lucide-react";

export function Methodology() {
  const [openSection, setOpenSection] = useState<number | null>(null);

  useEffect(() => {
    setOpenSection(0);
  }, []);

  const sections = [
    {
      title: "1. Spaceborne Multi-Sensor Data Ingestion",
      icon: Cpu,
      summary:
        "Fusing 10m ESA Sentinel-2 MSI multispectral surface reflectance with NASA GEDI spaceborne full-waveform LiDAR and JAXA ALOS-2 PALSAR L-band SAR.",
      details: [
        "Atmospheric correction via Sen2Cor generating surface reflectance (Level-2A).",
        "Cloud, shadow, and aerosol masking via SCL (Scene Classification Layer).",
        "NASA GEDI RH98 canopy relative height calibration at 242 Hz footprint sampling.",
        "SAR HV cross-polarization to penetrate top foliage for accurate understory biomass estimation.",
      ],
    },
    {
      title: "2. Forest Stratification & Allometric Modeling",
      icon: TreePine,
      summary:
        "Biomass calculation applying peer-reviewed IPCC Tier-3 pan-tropical allometric equations (Chave et al., 2014) combined with localized ecoregion wood density tables.",
      details: [
        "Equation: AGB = 0.0673 × (ρ × H × D²)^0.976 calibrated with LiDAR RH98.",
        "Below-Ground Biomass (BGB) modeled via IPCC root-to-shoot ratio (R = 0.205).",
        "Total Organic Biomass = AGB + BGB.",
        "Total Carbon Stock = Total Biomass × Carbon Fraction (CF = 0.47).",
        "CO₂ Equivalent = Total Carbon Stock × (44 / 12).",
      ],
    },
    {
      title: "3. Uncertainty Quantification & Monte Carlo Validation",
      icon: BarChart4,
      summary:
        "Error propagation evaluated via 10,000-run Monte Carlo simulations modeling LiDAR footprint variance, allometric parameter residuals, and classification confidence.",
      details: [
        "Mean canopy height standard error: ±1.2m.",
        "Wood specific gravity (ρ) uncertainty interval: ±0.08 g/cm³.",
        "Cumulative carbon stock confidence interval: ±8.4% at the 95% confidence level.",
        "Compliant with Verra VCS VM0047 dynamic baseline requirements and Article 6 MRV standards.",
      ],
    },
    {
      title: "4. Carbon Credit Registry Pre-Feasibility",
      icon: FileCheck2,
      summary:
        "Translating carbon stock trajectories into verified emission reduction units (VERs) factoring registry buffer pool deductions, additionality, and permanence risk.",
      details: [
        "20% non-permanence buffer pool deduction applied to gross annual sequestration.",
        "Calculated using 10-year historical baseline deforestation rate from Hansen GFW data.",
        "Pre-feasibility compatible with Verra VCS, Gold Standard, and Plan Vivo methodologies.",
      ],
    },
  ];

  return (
    <div className="crystal-glass-card rounded-3xl shadow-2xl border border-white/20 p-6 sm:p-8 text-white space-y-6">
      {/* Section Title */}
      <div className="flex items-center gap-3 pb-4 border-b border-white/10">
        <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner">
          <Info className="w-5 h-5 text-emerald-400" />
        </div>
        <div>
          <h3 className="font-bold text-white text-lg tracking-tight">
            Scientific Methodology &amp; Mathematical Framework
          </h3>
          <p className="text-xs text-white/60">
            IPCC 2019 Refinement Tier 3 &amp; Verra VCS VM0047 Satellite MRV Architecture
          </p>
        </div>
      </div>

      {/* Accordion List */}
      <div className="space-y-3">
        {sections.map((section, idx) => {
          const isOpen = openSection === idx;
          const Icon = section.icon;

          return (
            <div
              key={idx}
              className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                isOpen
                  ? "border-emerald-400/40 crystal-glass shadow-lg"
                  : "border-white/10 crystal-glass hover:border-white/20"
              }`}
            >
              <button
                type="button"
                onClick={() => setOpenSection(isOpen ? null : idx)}
                className="w-full p-4 sm:p-5 flex items-center justify-between text-left gap-4"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2 rounded-xl border ${
                      isOpen
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
                        : "bg-white/5 text-white/70 border-white/10"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-bold text-sm sm:text-base text-white">
                      {section.title}
                    </h4>
                    <p className="text-xs text-white/60 mt-0.5 line-clamp-1">
                      {section.summary}
                    </p>
                  </div>
                </div>

                <div
                  className={`p-1 rounded-full transition-transform duration-200 ${
                    isOpen ? "rotate-180 text-emerald-400" : "text-white/40"
                  }`}
                >
                  <ChevronDown className="w-4 h-4" />
                </div>
              </button>

              {isOpen && (
                <div className="px-5 pb-5 pt-1 space-y-3 text-xs border-t border-white/5 text-white/80">
                  <p className="text-white/70 leading-relaxed bg-white/5 p-3 rounded-xl border border-white/5">
                    {section.summary}
                  </p>
                  <div className="space-y-1.5 pl-2">
                    <span className="font-semibold text-emerald-300 uppercase tracking-wider text-[10px] block mb-2">
                      Key Analytical Principles:
                    </span>
                    {section.details.map((detail, dIdx) => (
                      <div key={dIdx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span className="text-white/80">{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Methodology;
