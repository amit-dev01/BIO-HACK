import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  className?: string;
}

export function MetricCard({
  label,
  value,
  unit,
  subtext,
  className,
}: MetricCardProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardContent className="p-5">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate">
          {label}
        </p>
        <div className="flex items-baseline gap-1 mt-2">
          <span className="text-2xl font-bold font-mono text-forest">
            {value}
          </span>
          {unit && <span className="text-sm text-slate font-sans">{unit}</span>}
        </div>
        {subtext && <p className="text-xs text-slate mt-1">{subtext}</p>}
      </CardContent>
    </Card>
  );
}

export default MetricCard;

