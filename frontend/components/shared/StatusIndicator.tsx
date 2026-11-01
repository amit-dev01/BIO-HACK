import React from "react";
import { cn } from "@/lib/utils";

export type IndicatorStatus = "idle" | "drawing" | "configuring" | "loading" | "complete" | "error";

export interface StatusIndicatorProps {
  status: IndicatorStatus;
  label?: string;
  className?: string;
}

export function StatusIndicator({
  status,
  label,
  className,
}: StatusIndicatorProps) {
  const colorMap: Record<IndicatorStatus, string> = {
    idle: "bg-slate-400",
    drawing: "bg-amber-500",
    configuring: "bg-leaf",
    loading: "bg-blue-500 animate-pulse",
    complete: "bg-forest",
    error: "bg-destructive",
  };

  return (
    <div className={cn("inline-flex items-center gap-2 text-xs", className)}>
      <span className={cn("h-2.5 w-2.5 rounded-full", colorMap[status])} />
      {label && <span className="font-medium text-charcoal">{label}</span>}
    </div>
  );
}

export default StatusIndicator;

