"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

export interface DeforestationAlertBadgeProps {
  hasAlert: boolean;
  lossPct5Yr: number;
}

export function DeforestationAlertBadge({
  hasAlert,
  lossPct5Yr,
}: DeforestationAlertBadgeProps) {
  if (hasAlert) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1.5 py-1 px-3">
        <AlertTriangle className="h-4 w-4" />
        Deforestation Alert Detected ({lossPct5Yr}% 5-yr loss)
      </Badge>
    );
  }

  return (
    <Badge variant="secondary" className="flex items-center gap-1.5 py-1 px-3">
      <CheckCircle2 className="h-4 w-4" />
      Canopy Stable ({lossPct5Yr}% 5-yr variance)
    </Badge>
  );
}

export default DeforestationAlertBadge;

