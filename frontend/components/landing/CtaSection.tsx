"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Sparkles, TreePine, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export function CtaSection() {
  return (
    <section
      className="relative py-32 px-4 overflow-hidden bg-cover bg-center"
      style={{ backgroundImage: "url('/images/jungle-tropical.jpg')" }}
    >
      {/* Deep Forest Ambient Wash */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#05180A]/85 via-[#092813]/75 to-[#041408]/90" />

      {/* Floating Frosted Glass Sanctuary Card */}
      <div className="relative z-10 max-w-4xl mx-auto crystal-glass-card rounded-3xl p-10 sm:p-16 text-center border border-white/20 shadow-2xl space-y-7 text-white">
        {/* Specular sheen */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />

        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-semibold shadow-inner">
          <TreePine className="w-4 h-4 text-emerald-400" />
          <span>High-Integrity Carbon MRV</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>

        <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight drop-shadow-md">
          Ready to verify your forest <br className="hidden sm:inline" />
          carbon project?
        </h2>

        <p className="text-emerald-100/90 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed font-normal">
          Start assessing your conservation plots or carbon offset reserves with instant spaceborne satellite AI, allometric biomass inversion, and audit-ready reports.
        </p>

        <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
          <motion.div
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <Link
              href="/analyze"
              className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-base shadow-2xl shadow-emerald-950/70 border border-emerald-400/40 transition-all group"
            >
              <Sparkles className="w-5 h-5 text-emerald-200" />
              <span>Start Free Analysis</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>

        <div className="pt-6 border-t border-white/10 flex items-center justify-center gap-6 text-xs text-emerald-200/80 font-mono">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Verra VCS Aligned
          </span>
          <span>•</span>
          <span>Gold Standard MRV</span>
          <span>•</span>
          <span>IPCC Tier 3 Precision</span>
        </div>
      </div>
    </section>
  );
}

export default CtaSection;
