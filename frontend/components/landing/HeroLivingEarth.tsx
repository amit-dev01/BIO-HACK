"use client";

import React, { useEffect, useRef } from "react";
import { useAnimationEngine } from "@/context/AnimationContext";

export function HeroLivingEarth() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const { level, isReduced } = useAnimationEngine();

  // Layer 3: Floating Spores / Fireflies Canvas Simulation (Speed Increased & Silky Smooth)
  useEffect(() => {
    if (isReduced) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 600);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.parentElement?.clientWidth || window.innerWidth;
      height = canvas.height = canvas.parentElement?.clientHeight || 600;
    };
    window.addEventListener("resize", handleResize);

    const count = level === "reduced" ? 14 : 32;
    const spores = Array.from({ length: count }, () => {
      const randColor = Math.random();
      const color =
        randColor < 0.7
          ? "#A5D6A7" // 70% soft green
          : randColor < 0.9
          ? "#FFD54F" // 20% warm amber
          : "#FFFFFF"; // 10% soft white

      return {
        x: Math.random() * width,
        y: Math.random() * height,
        baseX: Math.random() * width,
        size: Math.random() * 3.5 + 2, // 2-5.5px
        speedY: Math.random() * 1.5 + 0.9, // 2x speed increase (5-8s viewport crossing)
        driftAmp: Math.random() * 30 + 12,
        driftFreq: Math.random() * 0.0028 + 0.0016, // faster organic harmonic oscillation
        seed: Math.random() * 1000,
        opacityMax: Math.random() * 0.45 + 0.35,
        color,
      };
    });

    const render = (time: number) => {
      ctx.clearRect(0, 0, width, height);

      for (const p of spores) {
        p.y -= p.speedY;
        p.x = p.baseX + Math.sin(time * p.driftFreq + p.seed) * p.driftAmp;

        // Fade in at bottom, fade out at top (smooth curve)
        const relY = p.y / height;
        let alpha = p.opacityMax;
        if (relY > 0.82) alpha = ((1 - relY) / 0.18) * p.opacityMax;
        else if (relY < 0.18) alpha = (relY / 0.18) * p.opacityMax;

        if (p.y < -12) {
          p.y = height + 12;
          p.baseX = Math.random() * width;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
        ctx.shadowBlur = 10;
        ctx.shadowColor = p.color;
        ctx.fill();
      }

      animId = requestAnimationFrame(render);
    };

    animId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
    };
  }, [level, isReduced]);

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden select-none z-0">
      {/* Layer 1: Semi-Transparent Cloud Drift Blobs (Tropospheric Parallax) */}
      <div className="absolute inset-0 opacity-15 blur-3xl will-change-transform animate-cloud-drift-a">
        <svg viewBox="0 0 1200 600" className="w-[220vw] h-full fill-white/80">
          <path d="M150,300 Q300,200 450,320 T750,280 T1050,350 T1350,260 L1350,600 L0,600 Z" />
        </svg>
      </div>
      <div className="absolute inset-0 opacity-10 blur-2xl will-change-transform animate-cloud-drift-b">
        <svg viewBox="0 0 1200 600" className="w-[180vw] h-full fill-emerald-100/60">
          <path d="M100,400 Q280,260 480,380 T880,310 T1280,410 L1280,600 L0,600 Z" />
        </svg>
      </div>

      {/* Layer 2: Living Wild Dense Jungle Rainforest (100% Crystal Vivid Jungle Trees & Canopy) */}
      <div
        className="absolute inset-0 bg-cover bg-center animate-canopy-breathe will-change-transform opacity-100"
        style={{
          backgroundImage: "url('/images/jungle-dense.jpg')",
          transformOrigin: "center center",
        }}
      />
      {/* Soft Sunlight & Atmospheric Emerald Tint */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/40" />

      {/* Layer 3: Floating Spores / Fireflies Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 z-10 w-full h-full" />

      {/* Layer 4: Diagonal Crepuscular Light Beams (God Rays through canopy) */}
      <div className="absolute inset-0 z-20 mix-blend-screen pointer-events-none animate-light-ray-drift">
        <div className="absolute -top-32 left-1/4 w-36 h-[150vh] -rotate-[22deg] bg-gradient-to-b from-white/12 via-white/5 to-transparent blur-2xl" />
        <div className="absolute -top-32 left-2/3 w-48 h-[150vh] -rotate-[18deg] bg-gradient-to-b from-amber-200/10 via-white/4 to-transparent blur-3xl" />
      </div>

      {/* Layer 5: Subtle Cinematic Vignette */}
      <div className="absolute inset-0 z-30 animate-vignette-pulse bg-[radial-gradient(ellipse_at_center,transparent_45%,rgba(3,7,18,0.45)_100%)]" />
    </div>
  );
}

export default HeroLivingEarth;
