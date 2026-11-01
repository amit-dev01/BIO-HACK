"use client";

import React from "react";
import { ShieldCheck, Info } from "lucide-react";

interface ConfidenceBadgeProps {
  score: number;
  label: string;
}

export function ConfidenceBadge({ score, label }: ConfidenceBadgeProps) {
  let colorStyles = "bg-green-100 text-green-800 border-green-200";
  if (score < 60) {
    colorStyles = "bg-red-100 text-red-800 border-red-200";
  } else if (score <= 80) {
    colorStyles = "bg-amber-100 text-amber-800 border-amber-200";
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold shadow-xs ${colorStyles}`}
      title="Composite verification score based on LiDAR coverage, optical cloud cover, and spatial resolution."
    >
      <ShieldCheck className="w-3.5 h-3.5" />
      <span>{label}</span>
      <span className="font-mono opacity-80">({score}/100)</span>
    </div>
  );
}

export default ConfidenceBadge;

