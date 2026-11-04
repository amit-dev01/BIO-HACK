"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, Trees, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { HeroLivingEarth } from "@/components/landing/HeroLivingEarth";

export function HeroSection() {
  return (
    <section className="relative min-h-[88vh] flex items-center justify-center py-28 px-4 text-center overflow-hidden bg-transparent text-white">
      {/* Animation 1: Living Forest from Space (5-Layer System with 100% Vivid Jungle Wallpaper) */}
      <HeroLivingEarth />

      <div className="relative z-20 max-w-4xl mx-auto space-y-7">
        {/* Animated Badge */}
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full crystal-glass text-emerald-300 text-xs font-bold shadow-xl border border-white/30 backdrop-blur-xl"
        >
          <Trees className="h-4 w-4 text-emerald-300 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
          <span>Next-Gen Jungle MRV &amp; Carbon Accounting</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
        </motion.div>

        {/* Cinematic Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="text-5xl font-black tracking-tight text-white sm:text-6xl lg:text-7xl leading-[1.1] drop-shadow-md"
        >
          High-Resolution Forest <br />
          <span className="bg-gradient-to-r from-emerald-400 via-green-300 to-amber-300 bg-clip-text text-transparent">
            Carbon Intelligence
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.16, duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="text-lg sm:text-xl text-emerald-100/90 max-w-2xl mx-auto font-normal leading-relaxed drop-shadow-sm"
        >
          Accurate biomass estimation, canopy height analysis, and Verra-compliant carbon stock verification powered by Sentinel-2, GEDI, and AI models.
        </motion.p>

        {/* Action Button */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.24, duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-wrap justify-center gap-4 pt-4"
        >
          <motion.div
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 450, damping: 25 }}
          >
            <Link
              href="/analyze"
              className="relative inline-flex items-center gap-3 px-8 py-4 rounded-2xl crystal-glass-btn text-white font-black text-base shadow-2xl overflow-hidden group transition-all"
            >
              {/* Specular Light Sweep on Hover */}
              <span className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-500 bg-gradient-to-r from-transparent via-white/25 to-transparent pointer-events-none" />
              <Sparkles className="w-5 h-5 text-green-200" />
              <span>Launch Analysis</span>
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

export default HeroSection;
