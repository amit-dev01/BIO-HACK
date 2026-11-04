"use client";

import React, { useEffect, useState, useRef } from "react";
import { useInView } from "framer-motion";

interface StatItemProps {
  target: number;
  prefix?: string;
  suffix?: string;
  label: string;
  delayMs: number;
  accentColor: string;
  flashColor: string;
}

function AnimatedImpactStat({
  target,
  prefix = "",
  suffix = "",
  label,
  delayMs,
  accentColor,
  flashColor,
}: StatItemProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(containerRef, { once: true, amount: 0.3 });
  const [value, setValue] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [isFlashing, setIsFlashing] = useState(false);

  useEffect(() => {
    if (!isInView) return;

    const timeout = setTimeout(() => {
      const startTime = performance.now();
      const duration = 1100; // Increased speed from 2000ms -> 1100ms for fluid, snappy counting

      const frame = (now: number) => {
        const elapsed = now - startTime;
        const progress = Math.min(1, elapsed / duration);
        // Snappy organic cubic deceleration: 1 - (1 - progress)^3
        const eased = 1 - Math.pow(1 - progress, 3);
        setValue(Math.floor(eased * target));

        if (progress < 1) {
          requestAnimationFrame(frame);
        } else {
          setValue(target);
          setIsFinished(true);
          setIsFlashing(true);
          setTimeout(() => setIsFlashing(false), 250);
        }
      };

      requestAnimationFrame(frame);
    }, delayMs);

    return () => clearTimeout(timeout);
  }, [isInView, target, delayMs]);

  return (
    <div
      ref={containerRef}
      className="crystal-glass-card rounded-3xl p-8 text-center relative flex flex-col items-center justify-center transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 group border border-white/20 text-white"
    >
      {/* Specular Top Sheen */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />

      {/* Sonar Ping Ring Expanding 1x to 3x on Completion (Snappy 0.45s) */}
      {isFinished && (
        <span className="absolute w-32 h-32 rounded-full border-2 border-emerald-400 animate-sonar-ping pointer-events-none" />
      )}

      {/* Number Display with Color Flash */}
      <div
        className="text-4xl sm:text-5xl lg:text-6xl font-black font-mono tracking-tight transition-colors duration-250 drop-shadow-md"
        style={{ color: isFlashing ? flashColor : accentColor }}
      >
        {prefix}
        {value.toLocaleString()}
        {suffix}
      </div>

      <div className="text-xs uppercase tracking-wider text-emerald-100/80 font-bold mt-3 max-w-[220px] leading-relaxed">
        {label}
      </div>
    </div>
  );
}

export function MetricsPreview() {
  return (
    <section className="py-20 px-4 relative z-10 overflow-hidden bg-transparent">
      {/* Ambient forest light aura */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(76,175,80,0.15)_0%,transparent_70%)]" />

      <div className="max-w-6xl mx-auto relative z-10">
        <div className="text-center mb-10 space-y-2">
          <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-[11px] uppercase tracking-widest text-emerald-300 font-bold bg-emerald-500/20 backdrop-blur-md border border-emerald-400/30 shadow-xs">
            Verified Global Forest Impact
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight drop-shadow-md">
            Satellite Intelligence at Planetary Scale
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Stat 1: 90% */}
          <AnimatedImpactStat
            target={90}
            suffix="%"
            label="Verification Cost Reduction"
            delayMs={0}
            accentColor="#4ADE80"
            flashColor="#86EFAC"
          />

          {/* Stat 2: $100K+ */}
          <AnimatedImpactStat
            target={100}
            prefix="$"
            suffix="K+"
            label="Average Audit Savings / Project"
            delayMs={150}
            accentColor="#FBBF24"
            flashColor="#FDE68A"
          />

          {/* Stat 3: 370M */}
          <AnimatedImpactStat
            target={370}
            suffix="M"
            label="Hectares of Verified Forest Canopy"
            delayMs={300}
            accentColor="#34D399"
            flashColor="#A7F3D0"
          />
        </div>
      </div>
    </section>
  );
}

export default MetricsPreview;
