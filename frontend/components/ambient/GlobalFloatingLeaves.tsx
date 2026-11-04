"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { useAnimationEngine } from "@/context/AnimationContext";

export function GlobalFloatingLeaves() {
  const { level } = useAnimationEngine();
  const pathname = usePathname();

  // Exclude active map analysis screen so the canvas remains completely distraction-free
  if (level === "none" || pathname.startsWith("/analyze")) {
    return null;
  }

  const leaves = [
    { size: 26, left: "8%", duration: 22, delay: 0, opacity: 0.08 },
    { size: 18, left: "34%", duration: 30, delay: 5, opacity: 0.06 },
    { size: 22, left: "68%", duration: 26, delay: 11, opacity: 0.07 },
    { size: 16, left: "86%", duration: 34, delay: 3, opacity: 0.05 },
  ];

  const activeLeaves = level === "reduced" ? leaves.slice(0, 2) : leaves;

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden select-none">
      {activeLeaves.map((leaf, idx) => (
        <div
          key={idx}
          className="absolute -top-12 animate-leaf-fall will-change-transform"
          style={{
            left: leaf.left,
            animationDuration: `${leaf.duration}s`,
            animationDelay: `${leaf.delay}s`,
            opacity: leaf.opacity,
          }}
        >
          <svg width={leaf.size} height={leaf.size} viewBox="0 0 24 24" fill="#4CAF50">
            <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75C7 8 17 8 17 8z" />
          </svg>
        </div>
      ))}
    </div>
  );
}

export default GlobalFloatingLeaves;

