"use client";

import React from "react";
import { Progress } from "@/components/ui/progress";
import { ANALYSIS_PROGRESS_STAGES } from "@/lib/mock-data";
import { CheckCircle2, Loader2 } from "lucide-react";

export interface ProgressOverlayProps {
  currentStep: number;
}

export function ProgressOverlay({ currentStep }: ProgressOverlayProps) {
  const percentage = Math.min(Math.round((currentStep / 5) * 100), 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-white rounded-card p-6 shadow-xl border border-border">
        <h3 className="text-xl font-bold text-forest mb-2">Analyzing Forest Area</h3>
        <p className="text-xs text-slate mb-4">
          Running spatial algorithms and multi-temporal satellite processing...
        </p>

        <Progress value={percentage} className="h-2 mb-4" />

        <div className="space-y-3">
          {ANALYSIS_PROGRESS_STAGES.map((stage) => {
            const isCompleted = currentStep > stage.step_number;
            const isCurrent = currentStep === stage.step_number;

            return (
              <div
                key={stage.step_number}
                className={`flex items-center gap-3 text-sm transition-opacity ${
                  isCompleted
                    ? "text-forest font-medium"
                    : isCurrent
                    ? "text-charcoal font-semibold"
                    : "text-slate/60"
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-forest" />
                ) : isCurrent ? (
                  <Loader2 className="h-4 w-4 animate-spin text-leaf" />
                ) : (
                  <div className="h-4 w-4 rounded-full border border-slate/30" />
                )}
                <span>{stage.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default ProgressOverlay;

