"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { TreePine, Check, Loader2, Sparkles, AlertTriangle, ArrowLeft } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";

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

export function AnalysisProgress() {
  const router = useRouter();
  const { state, dispatch } = useAnalysis();
  const { analysisStatus, progressStep, results } = state;

  const [factIndex, setFactIndex] = useState(0);

  // Rotate Did You Know facts every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setFactIndex((prev) => (prev + 1) % DID_YOU_KNOW_FACTS.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Handle completion and auto-redirect
  useEffect(() => {
    if (analysisStatus === "complete") {
      const targetId = results?.analysis_id || "cai_anlz_demo";
      const timer = setTimeout(() => {
        router.push(`/results/${targetId}`);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [analysisStatus, results, router]);

  if (analysisStatus !== "loading" && analysisStatus !== "complete" && analysisStatus !== "error") {
    return null;
  }

  const isFinished = analysisStatus === "complete";
  const overallPercent = Math.min(100, Math.round(((progressStep - 1) / 5) * 100 + (isFinished ? 100 : 15)));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl p-8 sm:p-12 max-w-lg w-full shadow-2xl text-center relative overflow-hidden border border-gray-100">
        {analysisStatus === "error" ? (
          /* Error Screen */
          <div className="py-6 flex flex-col items-center justify-center space-y-4 animate-in zoom-in-90 duration-300">
            <div className="w-16 h-16 rounded-full bg-red-100 border-4 border-red-500/30 flex items-center justify-center shadow-lg">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 tracking-tight">
              Analysis Failed
            </h2>
            <div className="bg-red-50 border border-red-200 text-red-800 text-xs sm:text-sm p-4 rounded-2xl max-w-sm text-left">
              <p className="font-semibold mb-1">Issue reported by satellite engine:</p>
              <p>{state.error || "Could not complete live satellite computation."}</p>
            </div>
            <p className="text-xs text-gray-500 max-w-sm">
              Please adjust your polygon on the map (must be between 10 ha and 100,000 ha) and try again.
            </p>
            <div className="pt-2 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  dispatch({ type: "SET_STATUS", payload: "idle" });
                  dispatch({ type: "SET_ERROR", payload: null });
                }}
                className="px-6 py-2.5 rounded-full bg-gray-900 text-white text-xs font-bold hover:bg-gray-800 transition-all flex items-center gap-2 shadow-lg"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Map
              </button>
            </div>
          </div>
        ) : isFinished ? (
          /* Success Burst Screen */
          <div className="py-8 flex flex-col items-center justify-center space-y-4 animate-in zoom-in-90 duration-300">
            <div className="w-20 h-20 rounded-full bg-green-100 border-4 border-green-500/30 flex items-center justify-center shadow-xl animate-bounce">
              <Check className="w-10 h-10 text-green-600 stroke-[3]" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">
              Analysis Complete!
            </h2>
            <p className="text-sm text-gray-500">
              Generating your interactive carbon intelligence dashboard...
            </p>
          </div>
        ) : (
          /* Running Stepper Screen */
          <div className="space-y-6">
            {/* Pulsing TreePine Icon */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="w-20 h-20 rounded-2xl bg-green-50 border border-green-200 flex items-center justify-center shadow-inner animate-[pulse_2s_ease-in-out_infinite]">
                  <TreePine className="w-10 h-10 text-green-600 transition-transform duration-700 scale-110" />
                </div>
                <div className="absolute -top-1 -right-1">
                  <span className="flex h-4 w-4 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-4 w-4 bg-green-600" />
                  </span>
                </div>
              </div>
            </div>

            {/* Header Titles */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 tracking-tight">
                Analyzing Your Forest
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                This typically takes about 15 seconds
              </p>
            </div>

            {/* 5-Step Stepper */}
            <div className="space-y-3.5 text-left pt-2">
              {STEPS.map((stepItem) => {
                const isComplete = progressStep > stepItem.step || isFinished;
                const isActive = progressStep === stepItem.step && !isFinished;
                const isPending = progressStep < stepItem.step;

                return (
                  <div key={stepItem.step} className="space-y-1">
                    <div className="flex items-center gap-3">
                      {/* Step Indicator Circle */}
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 shrink-0 ${
                          isComplete
                            ? "bg-green-600 text-white shadow-sm"
                            : isActive
                            ? "bg-green-500 text-white ring-4 ring-green-100"
                            : "bg-gray-100 text-gray-400"
                        }`}
                      >
                        {isComplete ? (
                          <Check className="w-4 h-4 stroke-[2.5]" />
                        ) : isActive ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          stepItem.step
                        )}
                      </div>

                      {/* Label Text */}
                      <span
                        className={`text-sm transition-colors duration-200 ${
                          isComplete
                            ? "text-gray-400 line-through"
                            : isActive
                            ? "text-gray-900 font-semibold"
                            : "text-gray-400"
                        }`}
                      >
                        {stepItem.label}
                      </span>
                    </div>

                    {/* Step Sub-Progress Bar */}
                    <div className="ml-10 h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${
                          isComplete
                            ? "w-full bg-green-600"
                            : isActive
                            ? "w-3/4 bg-green-500 animate-pulse"
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
              <div className="flex justify-between text-xs text-gray-400 mb-1 font-mono">
                <span>Progress</span>
                <span>{overallPercent}%</span>
              </div>
              <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-green-600 transition-all duration-300 rounded-full"
                  style={{ width: `${overallPercent}%` }}
                />
              </div>
            </div>

            {/* Pulsing "Did you know?" Fact */}
            <div className="pt-3 border-t border-gray-100 min-h-[50px] flex items-center justify-center">
              <div className="flex items-center gap-2 text-xs text-gray-400 italic animate-in fade-in duration-500 key={factIndex}">
                <Sparkles className="w-3.5 h-3.5 text-green-500 shrink-0 not-italic" />
                <span>
                  <strong className="text-gray-600 not-italic font-semibold">
                    Did you know?{" "}
                  </strong>
                  {DID_YOU_KNOW_FACTS[factIndex]}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisProgress;

