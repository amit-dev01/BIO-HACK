"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Props {
  centroid: { x: number; y: number } | null;
  areaHa: number | null;
  polygonTriggerKey?: string | number;
}

export function PolygonCelebrationLayer({ centroid, areaHa, polygonTriggerKey }: Props) {
  const [showBurst, setShowBurst] = useState(false);

  useEffect(() => {
    if (centroid && areaHa) {
      setShowBurst(true);
      const timer = setTimeout(() => setShowBurst(false), 900);
      return () => clearTimeout(timer);
    }
  }, [centroid, areaHa, polygonTriggerKey]);

  if (!centroid || !areaHa) return null;

  // 10 leaf particles in radial distribution
  const burstParticles = Array.from({ length: 10 }).map((_, i) => {
    const angle = (i / 10) * Math.PI * 2 + (Math.random() * 0.4 - 0.2);
    const distance = 60 + Math.random() * 50;
    const colors = ["#4CAF50", "#2E7D32", "#FFB74D", "#81C784", "#FFA000"];
    return {
      dx: Math.cos(angle) * distance,
      dy: Math.sin(angle) * distance,
      rot: (Math.random() > 0.5 ? 1 : -1) * (180 + Math.random() * 180),
      color: colors[i % colors.length],
    };
  });

  return (
    <div className="absolute inset-0 pointer-events-none z-30 overflow-hidden select-none">
      <div
        style={{
          position: "absolute",
          left: centroid.x,
          top: centroid.y,
        }}
      >
        <AnimatePresence>
          {showBurst && (
            <>
              {/* 1. Water Drop Expanding Ripple Wave (Snappy 0.5s) */}
              <motion.div
                initial={{ scale: 0, opacity: 0.4 }}
                animate={{ scale: 3.5, opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="absolute -top-16 -left-16 w-32 h-32 rounded-full border-2 border-emerald-400 bg-emerald-500/15"
              />

              {/* 2. Centrifugal Leaf Particles Dispersal (Fast & Silky 0.45s) */}
              {burstParticles.map((p, idx) => (
                <motion.div
                  key={idx}
                  initial={{ x: 0, y: 0, scale: 0, rotate: 0, opacity: 1 }}
                  animate={{
                    x: p.dx,
                    y: p.dy,
                    scale: [0, 1.25, 0.8],
                    rotate: p.rot,
                    opacity: 0,
                  }}
                  transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                  className="absolute -top-1.5 -left-3 w-4 h-2 rounded-full shadow-xs"
                  style={{ backgroundColor: p.color }}
                />
              ))}
            </>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default PolygonCelebrationLayer;
