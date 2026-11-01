import * as React from "react";
import { Badge } from "@/components/ui/badge";

export interface ConfidenceBadgeProps {
  score: number;
  label: string;
}

export function ConfidenceBadge({ score, label }: ConfidenceBadgeProps) {
  const variant =
    score >= 90 ? "success" : score >= 75 ? "secondary" : "warning";

  return (
    <Badge variant={variant} className="font-mono text-xs">
      {label} ({score}%)
    </Badge>
  );
}

export default ConfidenceBadge;
