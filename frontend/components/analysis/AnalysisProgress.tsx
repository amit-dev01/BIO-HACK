"use client";

import React, { useEffect, useState, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import { TreePine, AlertTriangle, ArrowLeft, Sparkles } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";
import { useAnimationEngine } from "@/context/AnimationContext";
import { motion, AnimatePresence } from "framer-motion";

const DID_YOU_KNOW_FACTS = [
  "One hectare of tropical forest can store up to 200 tonnes of living carbon.",
  "NASA GEDI fires 242 laser pulses per second from the ISS to map canopy height in 3D.",
  "Forest carbon projects protect biodiversity for over 80% of terrestrial wildlife species.",
  "Multi-sensor remote sensing detects canopy degradation at 10-meter precision.",
  "High-integrity satellite MRV reduces carbon project verification costs by over 70%.",
];

const STEPS = [
  { step: 1, label: "Fetching satellite imagery..." },
  { step: 2, label: "Analyzing canopy cover..." },
  { step: 3, label: "Estimating biomass..." },
  { step: 4, label: "Calculating carbon stock..." },
  { step: 5, label: "Generating report..." },
];

// Telemetry stream tokens for the background matrix
const TELEMETRY_TOKENS = [
  "NDVI 0.842",
  "11.138°N 76.440°E",
  "GEDI-2A 242Hz",
  "SWIR-2 2.2μm",
  "184 tC/ha",
  "MSI_B08 842nm",
  "IPCC_Tier_3",
  "CANOPY 88.4%",
  "EVI 0.618",
  "STRATA_HIGH",
  "S2B_MSIL2A",
  "ALOS-2 PALSAR",
];

// Confetti leaf definition
interface ConfettiLeaf {
  id: number;
  x: number;
  delay: number;
  rotation: number;
  size: number;
  color: string;
}

export function AnalysisProgress() {
  const router = useRouter();
  const { state, dispatch } = useAnalysis();
  const { analysisStatus, progressStep, results } = state;
  const { isReduced, level } = useAnimationEngine();

  const [factIndex, setFactIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [showShockwave, setShowShockwave] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  // Generate random confetti leaves once
  const confettiLeaves: ConfettiLeaf[] = useMemo(() => {
    return Array.from({ length: 18 }).map((_, i) => ({
      id: i,
      x: Math.random() * 100, // percentage across modal
      delay: Math.random() * 0.4,
      rotation: Math.random() * 360,
      size: 14 + Math.random() * 12,
      color: i % 3 === 0 ? "#4CAF50" : i % 3 === 1 ? "#2E7D32" : "#81C784",
    }));
  }, []);

  // Track completed steps and trigger particle bursts
  useEffect(() => {
    if (progressStep > 1) {
      setCompletedSteps((prev) => {
        const newlyDone: number[] = [];
        for (let i = 1; i < progressStep; i++) {
          if (!prev.includes(i)) newlyDone.push(i);
        }
        return [...prev, ...newlyDone];
      });
    }
  }, [progressStep]);

  // Rotate Did You Know facts every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex((prev) => (prev + 1) % DID_YOU_KNOW_FACTS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Handle completion sequence (bounce -> shockwave -> leaf confetti -> redirect)
  useEffect(() => {
    if (analysisStatus === "complete") {
      setShowShockwave(true);
      setShowConfetti(true);

      const timer = setTimeout(() => {
        router.push("/results");
      }, 850);
      return () => clearTimeout(timer);
    }
  }, [analysisStatus, results, router]);

  if (analysisStatus !== "loading" && analysisStatus !== "complete" && analysisStatus !== "error") {
    return null;
  }

  const isFinished = analysisStatus === "complete";
  const overallPercent = Math.min(
    100,
    Math.round(((progressStep - 1) / 5) * 100 + (isFinished ? 100 : 15))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md overflow-hidden animate-in fade-in duration-300">
      {/* 1. Subtle 24fps Grain / Processing Noise */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.035] mix-blend-overlay"
        style={{
          backgroundImage: `radial-gradient(#4CAF50 1px, transparent 1px)`,
          backgroundSize: "24px 24px",
        }}
      />

      {/* 2. Forest Telemetry Data Stream (Matrix Rain - 5% opacity) */}
      {!isReduced && (
        <div className="pointer-events-none absolute inset-0 overflow-hidden flex justify-between px-6 opacity-[0.06] select-none text-[11px] font-mono text-green-400">
          {[0, 1, 2, 3, 4, 5].map((colIndex) => (
            <div
              key={colIndex}
              className="flex flex-col space-y-4 animate-[dataStream_18s_linear_infinite]"
              style={{
                animationDelay: `${colIndex * -3}s`,
                transform: "translateY(-50%)",
              }}
            >
              {[...TELEMETRY_TOKENS, ...TELEMETRY_TOKENS, ...TELEMETRY_TOKENS].map((item, idx) => (
                <span key={idx} className="block whitespace-nowrap">
                  {item}
                </span>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* 3. Central Ambient Glowing Orb (200px diameter, 3s loop) */}
      <div
        className="pointer-events-none absolute w-[280px] h-[280px] rounded-full blur-3xl opacity-30"
        style={{
          background: "radial-gradient(circle, rgba(76,175,80,0.5) 0%, rgba(27,94,32,0) 70%)",
          animation: !isReduced ? "orbBreathe 3s ease-in-out infinite" : "none",
        }}
      />

      {/* 4. Orbiting Rings (3 concentric 3D-perspective rings) */}
      {!isReduced && (
        <div className="pointer-events-none absolute flex items-center justify-center [perspective:800px]">
          {/* Ring 1: 340px clockwise 8s */}
          <div
            className="absolute rounded-full border border-green-500/20"
            style={{
              width: "360px",
              height: "360px",
              animation: "orbitSpinCW 8s linear infinite",
            }}
          />
          {/* Ring 2: 440px counter-clockwise 12s, tilted 30deg */}
          <div
            className="absolute rounded-full border border-green-400/20"
            style={{
              width: "460px",
              height: "460px",
              transform: "rotateX(60deg) rotateY(30deg)",
              animation: "orbitSpinCCW 12s linear infinite",
            }}
          />
          {/* Ring 3: 260px clockwise 6s, tilted -20deg */}
          <div
            className="absolute rounded-full border border-green-300/15"
            style={{
              width: "280px",
              height: "280px",
              transform: "rotateX(-45deg) rotateY(-20deg)",
              animation: "orbitSpinCW 6s linear infinite",
            }}
          />
        </div>
      )}

      {/* 5. Bright Green Shockwave Ring upon Complete */}
      <AnimatePresence>
        {showShockwave && !isReduced && (
          <motion.div
            initial={{ scale: 0.1, opacity: 0.85 }}
            animate={{ scale: 5, opacity: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="pointer-events-none absolute w-64 h-64 rounded-full border-4 border-green-400 shadow-[0_0_50px_#4CAF50]"
          />
        )}
      </AnimatePresence>

      {/* 6. Main Modal Card with Settle Bounce */}
      <motion.div
        initial={{ opacity: 0, scale: 0.94, y: 15 }}
        animate={{
          opacity: 1,
          scale: isFinished ? [1, 1.025, 1] : 1,
          y: 0,
        }}
        transition={{
          duration: isFinished ? 0.35 : 0.4,
          ease: [0.16, 1, 0.3, 1],
        }}
        className="crystal-glass-card rounded-3xl p-8 sm:p-11 max-w-lg w-full shadow-2xl text-center relative overflow-hidden border border-white/20 z-10 text-white"
      >
        {/* Top Specular Shimmer */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1.5px] bg-gradient-to-r from-transparent via-white/70 to-transparent" />

        {/* Leaf Confetti Cascade across Card on Completion */}
        {showConfetti && !isReduced && (
          <div className="pointer-events-none absolute inset-0 overflow-hidden z-20">
            {confettiLeaves.map((leaf) => (
              <motion.div
                key={leaf.id}
                initial={{
                  x: `${leaf.x}%`,
                  y: -30,
                  opacity: 0,
                  rotate: leaf.rotation,
                }}
                animate={{
                  y: 450,
                  opacity: [0, 1, 1, 0],
                  rotate: leaf.rotation + 360,
                }}
                transition={{
                  duration: 1.5,
                  delay: leaf.delay,
                  ease: "easeInOut",
                }}
                className="absolute"
              >
                <svg
                  width={leaf.size}
                  height={leaf.size}
                  viewBox="0 0 24 24"
                  fill="none"
                  style={{ color: leaf.color }}
                >
                  <path
                    d="M12 2C6.5 2 2 6.5 2 12C2 17.5 6.5 22 12 22C17.5 22 22 17.5 22 12C22 6.5 17.5 2 12 2ZM12 20C7.6 20 4 16.4 4 12C4 7.6 7.6 4 12 4C16.4 4 20 7.6 20 12C20 16.4 16.4 20 12 20Z"
                    fill="currentColor"
                    opacity="0.25"
                  />
                  <path
                    d="M17 7C14 7 8 9 6 18C15 16 17 10 17 7Z"
                    fill="currentColor"
                  />
                </svg>
              </motion.div>
            ))}
          </div>
        )}

        {analysisStatus === "error" ? (
          /* Error Screen */
          <div className="py-6 flex flex-col items-center justify-center space-y-4 animate-in zoom-in-95 duration-300">
            <div className="w-16 h-16 rounded-full bg-red-500/20 border-4 border-red-500/40 flex items-center justify-center shadow-lg">
              <AlertTriangle className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              Analysis Failed
            </h2>
            <div className="bg-red-500/20 border border-red-400/30 text-red-200 text-xs sm:text-sm p-4 rounded-2xl max-w-sm text-left">
              <p className="font-semibold mb-1 text-red-300">Issue reported by satellite engine:</p>
              <p>{state.error || "Could not complete live satellite computation."}</p>
            </div>
            <p className="text-xs text-white/60 max-w-sm">
              Please adjust your polygon on the map (must be between 10 ha and 100,000 ha) and try again.
            </p>
            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  dispatch({ type: "SET_STATUS", payload: "idle" });
                  dispatch({ type: "SET_ERROR", payload: null });
                }}
                className="px-6 py-2.5 rounded-full bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-500 transition-all flex items-center gap-2 shadow-lg"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Map
              </button>
            </div>
          </div>
        ) : isFinished ? (
          /* Success Burst Screen */
          <div className="py-8 flex flex-col items-center justify-center space-y-4">
            <motion.div
              initial={{ scale: 0.4, rotate: -20 }}
              animate={{ scale: [0.4, 1.25, 1.0], rotate: 0 }}
              transition={{ duration: 0.5, ease: [0.175, 0.885, 0.32, 1.275] }}
              className="w-20 h-20 rounded-full bg-emerald-500/20 border-4 border-emerald-400/40 flex items-center justify-center shadow-xl relative"
            >
              <svg className="w-10 h-10 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <motion.path
                  d="M20 6L9 17L4 12"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                />
              </svg>
            </motion.div>
            <h2 className="text-3xl font-bold text-white tracking-tight">
              Analysis Complete!
            </h2>
            <p className="text-sm text-emerald-100/70">
              Generating your interactive carbon intelligence dashboard...
            </p>
          </div>
        ) : (
          /* Running Stepper Screen */
          <div className="space-y-6">
            {/* Pulsing TreePine Icon with organic respiration */}
            <div className="flex justify-center">
              <div className="relative">
                <motion.div
                  animate={
                    !isReduced
                      ? {
                          scale: [1, 1.06, 1],
                          boxShadow: [
                            "0 0 0 rgba(76,175,80,0)",
                            "0 0 24px rgba(76,175,80,0.3)",
                            "0 0 0 rgba(76,175,80,0)",
                          ],
                        }
                      : {}
                  }
                  transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
                  className="w-20 h-20 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center shadow-xl shadow-emerald-950/50"
                >
                  <TreePine className="w-10 h-10 text-emerald-300 drop-shadow-[0_0_12px_rgba(52,211,153,0.8)] transition-transform duration-700" />
                </motion.div>
                <div className="absolute -top-1 -right-1">
                  <span className="flex h-4 w-4 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500" />
                  </span>
                </div>
              </div>
            </div>

            {/* Header Titles */}
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight">
                Analyzing Your Forest
              </h2>
              <p className="text-sm text-emerald-100/70 mt-1">
                Extracting multi-spectral reflectances &amp; LiDAR canopy heights
              </p>
            </div>

            {/* 5-Step Stepper with Self-Drawing SVG Checkmarks & Particle Bursts */}
            <div className="space-y-3.5 text-left pt-2">
              {STEPS.map((stepItem) => {
                const isComplete = progressStep > stepItem.step || isFinished;
                const isActive = progressStep === stepItem.step && !isFinished;

                return (
                  <div key={stepItem.step} className="space-y-1">
                    <div className="flex items-center gap-3 relative">
                      {/* Step Indicator Circle */}
                      <div className="relative">
                        <motion.div
                          animate={
                            isActive && !isReduced
                              ? { scale: [1, 1.08, 1] }
                              : { scale: 1 }
                          }
                          transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            ease: "easeInOut",
                          }}
                          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 shrink-0 ${
                            isComplete
                              ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/40"
                              : isActive
                              ? "bg-emerald-500 text-white ring-4 ring-emerald-400/30 shadow-lg shadow-emerald-500/50"
                              : "bg-white/10 text-white/50 border border-white/10"
                          }`}
                        >
                          {isComplete ? (
                            <svg
                              className="w-4 h-4 stroke-[2.5]"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <motion.path
                                d="M20 6L9 17L4 12"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 0.35, ease: "easeOut" }}
                              />
                            </svg>
                          ) : (
                            stepItem.step
                          )}
                        </motion.div>

                        {/* Particle Burst on Newly Completed Step */}
                        {isComplete && !isReduced && (
                          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                            {[0, 60, 120, 180, 240, 300].map((deg) => (
                              <motion.span
                                key={deg}
                                initial={{ scale: 1, x: 0, y: 0, opacity: 0.9 }}
                                animate={{
                                  x: Math.cos((deg * Math.PI) / 180) * 18,
                                  y: Math.sin((deg * Math.PI) / 180) * 18,
                                  scale: 0,
                                  opacity: 0,
                                }}
                                transition={{ duration: 0.45, ease: "easeOut" }}
                                className="absolute w-1.5 h-1.5 rounded-full bg-emerald-400"
                              />
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Label Text with Strikethrough draw */}
                      <div className="relative flex-1">
                        <span
                          className={`text-sm transition-colors duration-300 ${
                            isComplete
                              ? "text-white/50 font-normal"
                              : isActive
                              ? "text-white font-bold drop-shadow-sm"
                              : "text-white/40"
                          }`}
                        >
                          {stepItem.label}
                        </span>
                        {/* Strikethrough line animation */}
                        {isComplete && (
                          <motion.div
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                            className="absolute left-0 top-1/2 h-[1px] bg-emerald-400/40 origin-left w-full"
                          />
                        )}
                      </div>
                    </div>

                    {/* Step Sub-Progress Bar */}
                    <div className="ml-10 h-1 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 rounded-full ${
                          isComplete
                            ? "w-full bg-emerald-500"
                            : isActive
                            ? "w-3/4 bg-emerald-400 animate-pulse"
                            : "w-0"
                        }`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Overall Progress Bar */}
            <div className="pt-2">
              <div className="flex justify-between text-xs text-emerald-200/70 mb-1 font-mono">
                <span>Progress</span>
                <span>{overallPercent}%</span>
              </div>
              <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-green-400 shadow-[0_0_12px_rgba(52,211,153,0.6)] transition-all duration-300 rounded-full"
                  style={{ width: `${overallPercent}%` }}
                />
              </div>
            </div>

            {/* Pulsing "Did you know?" Fact */}
            <div className="pt-3 border-t border-white/10 min-h-[50px] flex items-center justify-center">
              <div className="flex items-center gap-2 text-xs text-white/80 italic animate-in fade-in duration-500 key={factIndex}">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0 not-italic" />
                <span>
                  <strong className="text-emerald-300 not-italic font-semibold">
                    Did you know?{" "}
                  </strong>
                  {DID_YOU_KNOW_FACTS[factIndex]}
                </span>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default AnalysisProgress;
