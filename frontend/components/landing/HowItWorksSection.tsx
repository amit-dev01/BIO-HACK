"use client";

import React from "react";
import { MousePointer, Satellite, Cpu, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

const steps = [
  {
    step: "01",
    title: "Draw Boundary or AOI",
    description: "Draw your forest tract on our 10m high-resolution satellite map or upload verified GIS GeoJSON shapefiles.",
    icon: MousePointer,
  },
  {
    step: "02",
    title: "Multi-Sensor Ingestion",
    description: "Our pipeline ingests multi-temporal Sentinel-2 imagery and GEDI LiDAR spaceborne canopy tracks.",
    icon: Satellite,
  },
  {
    step: "03",
    title: "AI Biomass Calculation",
    description: "Machine learning models estimate Above-Ground & Below-Ground Biomass and total carbon tonnage.",
    icon: Cpu,
  },
  {
    step: "04",
    title: "Verra-Grade Verification",
    description: "Download verified audit reports, uncertainty intervals, and carbon credit revenue projections.",
    icon: ShieldCheck,
  },
];

const cardVariants = {
  hidden: { opacity: 0, y: 32 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1, // snappy stagger
      duration: 0.38,
      ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
    },
  }),
};

const iconVariants = {
  hidden: { scale: 0.6, rotate: -8 },
  visible: (i: number) => ({
    scale: [0.6, 1.15, 1.0],
    rotate: [-8, 3, 0],
    transition: {
      delay: i * 0.1 + 0.18,
      duration: 0.28,
      ease: [0.34, 1.56, 0.64, 1.0] as [number, number, number, number],
    },
  }),
};

export function HowItWorksSection() {
  return (
    <section className="relative py-28 px-4 overflow-hidden bg-transparent text-white">
      {/* Background: Shifting diagonal organic ambient light gradient */}
      <div className="absolute inset-0 pointer-events-none opacity-30 bg-[radial-gradient(circle_at_0%_0%,rgba(76,175,80,0.18)_0%,transparent_50%),radial-gradient(circle_at_100%_100%,rgba(165,214,167,0.12)_0%,transparent_60%)] animate-pulse" />

      {/* Decorative Self-Drawing Connecting Dashed SVG Line */}
      <svg
        className="absolute top-1/2 left-0 w-full h-10 -translate-y-8 hidden lg:block pointer-events-none z-0"
        fill="none"
      >
        <motion.path
          d="M 180 20 H 1260"
          stroke="#4ADE80"
          strokeWidth="2"
          strokeDasharray="6 6"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 0.5 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ delay: 0.2, duration: 0.5, ease: "easeInOut" }}
        />
      </svg>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="text-center mb-16 space-y-3">
          <span className="text-xs uppercase tracking-widest text-emerald-300 font-bold bg-emerald-500/20 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-emerald-400/30 shadow-xs">
            Methodology &amp; Workflow
          </span>
          <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight drop-shadow-md">
            How CanopyAI Works
          </h2>
          <p className="text-sm text-emerald-100/80 max-w-xl mx-auto">
            From satellite orbit to verified carbon credit certification in four streamlined steps.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-7">
          {steps.map((item, idx) => (
            <motion.div
              key={idx}
              custom={idx}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
              variants={cardVariants}
              whileHover={{ y: -5, borderColor: "rgba(74, 222, 128, 0.6)" }}
              className="crystal-glass-card rounded-3xl p-7 border border-white/20 shadow-2xl transition-all relative flex flex-col justify-between group text-white"
            >
              {/* Specular sheen */}
              <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent" />

              <div>
                <div className="flex items-center justify-between mb-6">
                  <span className="text-3xl font-mono font-black text-emerald-400/80">
                    {item.step}
                  </span>
                  <motion.div
                    custom={idx}
                    variants={iconVariants}
                    className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 border border-emerald-400/30 shadow-inner group-hover:scale-110 group-hover:bg-emerald-500 group-hover:text-white transition-all duration-300"
                  >
                    <item.icon className="w-6 h-6" />
                  </motion.div>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                <p className="text-white/70 text-xs sm:text-sm leading-relaxed">{item.description}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-1.5 text-[11px] font-bold text-emerald-300 uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Phase {item.step}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorksSection;
