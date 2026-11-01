import React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface LoadingSpinnerProps {
  className?: string;
  size?: number;
}

export function LoadingSpinner({ className, size = 24 }: LoadingSpinnerProps) {
  return (
    <Loader2
      size={size}
      className={cn("animate-spin text-forest", className)}
    />
  );
}

export default LoadingSpinner;

