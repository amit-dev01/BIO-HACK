"use client";

import React, { useRef, useEffect } from "react";

export interface MapContainerProps {
  onPolygonCreated?: (polygon: GeoJSON.Feature<GeoJSON.Polygon>) => void;
}

export function MapContainer({ onPolygonCreated: _onPolygonCreated }: MapContainerProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Mapbox GL initialization will be attached here
  }, []);

  return (
    <div className="relative w-full h-full min-h-[500px] bg-slate-100 rounded-card overflow-hidden border border-border">
      <div ref={mapContainerRef} className="w-full h-full min-h-[500px]" />
      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1.5 rounded-button text-xs font-mono text-slate border">
        Mapbox GL v3 Container
      </div>
    </div>
  );
}

export default MapContainer;

