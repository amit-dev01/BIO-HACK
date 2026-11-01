"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAnalysis } from "@/context/AnalysisContext";

export function AnalysisConfigPanel() {
  const { state, setConfig, runAnalysis } = useAnalysis();

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg text-forest">Analysis Parameters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-xs font-semibold uppercase text-slate">Analysis Mode</label>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setConfig({ analysis_type: "quick" })}
              className={`flex-1 py-1.5 px-3 text-xs rounded-button border font-medium transition-colors ${
                state.analysisConfig.analysis_type === "quick"
                  ? "bg-forest text-white border-forest"
                  : "bg-white text-charcoal border-input"
              }`}
            >
              Quick (10m Optical)
            </button>
            <button
              onClick={() => setConfig({ analysis_type: "detailed" })}
              className={`flex-1 py-1.5 px-3 text-xs rounded-button border font-medium transition-colors ${
                state.analysisConfig.analysis_type === "detailed"
                  ? "bg-forest text-white border-forest"
                  : "bg-white text-charcoal border-input"
              }`}
            >
              Detailed (LiDAR + Radar)
            </button>
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold uppercase text-slate">Active Sensors</label>
          <div className="mt-2 space-y-1 text-xs text-charcoal">
            {state.analysisConfig.data_sources.map((src, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-leaf" />
                <span>{src}</span>
              </div>
            ))}
          </div>
        </div>

        <Button
          onClick={() => runAnalysis()}
          disabled={state.analysisStatus === "loading"}
          className="w-full mt-4"
        >
          {state.analysisStatus === "loading" ? "Analyzing..." : "Run Carbon Analysis"}
        </Button>
      </CardContent>
    </Card>
  );
}

export default AnalysisConfigPanel;

