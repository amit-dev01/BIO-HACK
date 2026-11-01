"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Square, Trash2, CheckCircle2 } from "lucide-react";

export interface DrawingControlsProps {
  onStartDraw?: () => void;
  onClear?: () => void;
  onConfirm?: () => void;
  isDrawing?: boolean;
}

export function DrawingControls({
  onStartDraw,
  onClear,
  onConfirm,
  isDrawing = false,
}: DrawingControlsProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-white rounded-button border border-border shadow-sm">
      <Button
        variant={isDrawing ? "secondary" : "outline"}
        size="sm"
        onClick={onStartDraw}
        className="flex items-center gap-1.5"
      >
        <Square className="h-4 w-4" />
        {isDrawing ? "Drawing Polygon..." : "Draw Area"}
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={onClear}
        className="flex items-center gap-1.5 text-destructive"
      >
        <Trash2 className="h-4 w-4" />
        Clear
      </Button>
      <Button
        variant="default"
        size="sm"
        onClick={onConfirm}
        className="flex items-center gap-1.5"
      >
        <CheckCircle2 className="h-4 w-4" />
        Confirm AOI
      </Button>
    </div>
  );
}

export default DrawingControls;

