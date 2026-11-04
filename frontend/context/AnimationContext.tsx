"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type AnimationLevel = "full" | "reduced" | "none";

interface AnimationContextType {
  level: AnimationLevel;
  isReduced: boolean;
}

const AnimationContext = createContext<AnimationContextType>({
  level: "full",
  isReduced: false,
});

export function AnimationProvider({ children }: { children: React.ReactNode }) {
  const [level, setLevel] = useState<AnimationLevel>("full");

  useEffect(() => {
    // 1. Accessibility: Check system prefers-reduced-motion
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (mediaQuery.matches) {
      setLevel("none");
      return;
    }

    // 2. Performance: Device memory & core check
    const nav = typeof navigator !== "undefined" ? (navigator as any) : null;
    const isLowMemory = nav?.deviceMemory && nav.deviceMemory < 4;
    const isLowCores = nav?.hardwareConcurrency && nav.hardwareConcurrency <= 4;

    if (isLowMemory || isLowCores) {
      setLevel("reduced");
    } else {
      setLevel("full");
    }

    const handleChange = () => {
      setLevel(mediaQuery.matches ? "none" : "full");
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return (
    <AnimationContext.Provider value={{ level, isReduced: level !== "full" }}>
      <div className={level === "none" ? "motion-reduce" : ""}>{children}</div>
    </AnimationContext.Provider>
  );
}

export const useAnimationEngine = () => useContext(AnimationContext);

