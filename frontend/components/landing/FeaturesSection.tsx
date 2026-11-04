"use client";

import React from "react";
import { Satellite, ShieldCheck, TrendingUp, Cpu, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const features = [
  {
    icon: Satellite,
    title: "Multi-Sensor Fusion",
    description:
      "Combines Sentinel-2 optical reflectances, GEDI LiDAR canopy profiles, and ALOS-2 radar backscatter for millimeter-level ecological precision.",
    tag: "Spaceborne",
  },
  {
    icon: Cpu,
    title: "AI Biomass Inversion",
    description:
      "Deep learning neural models calibrated on field-inventory plots deliver sub-hectare Above & Below Ground biomass estimates.",
    tag: "Neural Engine",
  },
  {
    icon: ShieldCheck,
    title: "Verra & Gold Standard MRV",
    description:
      "Audit-ready carbon calculations mapped directly to VM0007, VM0047, and IPCC Tier 3 rigorous accounting standards.",
    tag: "Certified",
  },
  {
    icon: TrendingUp,
    title: "NDVI Health & Loss Tracking",
    description:
      "Continuous disturbance tracking, 5-year historical vegetation health trajectories, and early deforestation warning alerts.",
    tag: "Longitudinal",
  },
];

export function FeaturesSection() {
  return (
    <section className="py-24 px-4 relative overflow-hidden bg-transparent text-white">
      {/* Ambient Forest Depth Wash */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(76,175,80,0.12)_0%,transparent_70%)]" />

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-[11px] uppercase tracking-widest text-emerald-300 font-bold bg-emerald-500/20 border border-emerald-400/30 shadow-xs backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            Ecological Precision
          </span>
          <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight drop-shadow-md">
            Engineered for Rigorous Carbon Accounting
          </h2>
          <p className="text-sm text-emerald-100/80 leading-relaxed max-w-xl mx-auto">
            Replace costly, slow manual tree tape measurements with spaceborne laser altimetry and multi-spectral satellite AI.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-7">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              whileHover={{ y: -6 }}
              transition={{ type: "spring", stiffness: 350, damping: 25 }}
              className="crystal-glass-card rounded-3xl p-7 flex flex-col justify-between transition-all duration-300 border border-white/20 hover:border-emerald-400/40 hover:shadow-2xl group text-white"
            >
              {/* Specular sheen */}
              <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent" />

              <div>
                <div className="flex items-center justify-between mb-5">
                  <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-400/30 shadow-inner group-hover:scale-110 group-hover:bg-emerald-500 group-hover:text-white transition-all duration-300">
                    <feature.icon className="h-6 w-6" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-emerald-300 bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                    {feature.tag}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-white mb-2 tracking-tight group-hover:text-emerald-300 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-xs sm:text-sm text-white/70 leading-relaxed">
                  {feature.description}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                <span>Verified Standard</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FeaturesSection;
