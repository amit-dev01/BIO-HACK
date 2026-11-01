"use client";

import React from "react";
import { UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface DroneUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFileSelect?: (file: File) => void;
}

export function DroneUploadModal({ isOpen, onClose }: DroneUploadModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-charcoal/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-white rounded-card p-6 shadow-xl border border-border">
        <h3 className="text-xl font-bold text-forest mb-2">Upload Drone Orthomosaic</h3>
        <p className="text-xs text-slate mb-6">
          Upload sub-decimeter GeoTIFF images for ultra-high-resolution canopy cover calibration.
        </p>

        <div className="border-2 border-dashed border-border rounded-card p-8 text-center hover:border-forest/50 cursor-pointer transition-colors">
          <UploadCloud className="h-10 w-10 text-slate mx-auto mb-3" />
          <p className="text-sm font-medium text-charcoal">Drag and drop GeoTIFF files</p>
          <p className="text-xs text-slate mt-1">Supports .tif, .tiff (up to 250MB)</p>
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={onClose}>Done</Button>
        </div>
      </div>
    </div>
  );
}

export default DroneUploadModal;

