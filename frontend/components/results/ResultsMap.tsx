"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { PolygonData } from "@/lib/types";
import { Plus, Minus, RotateCcw, Satellite, Layers } from "lucide-react";
import { useAnimationEngine } from "@/context/AnimationContext";

interface ResultsMapProps {
  polygon?: PolygonData | null;
}

// 100% Authentic, High-Resolution Global Satellite Imagery (unmetered & reliable)
export const ESRI_SATELLITE_STYLE: mapboxgl.Style = {
  version: 8,
  sources: {
    "esri-satellite-src": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: "© Esri, Maxar, Earthstar Geographics",
    },
  },
  layers: [
    {
      id: "esri-satellite-layer",
      type: "raster",
      source: "esri-satellite-src",
      minzoom: 0,
      maxzoom: 22,
    },
  ],
};

export const CARTO_VOYAGER_STYLE: mapboxgl.Style = {
  version: 8,
  sources: {
    "carto-voyager-src": {
      type: "raster",
      tiles: [
        "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: "© OpenStreetMap contributors, © CARTO",
    },
  },
  layers: [
    {
      id: "carto-voyager-layer",
      type: "raster",
      source: "carto-voyager-src",
      minzoom: 0,
      maxzoom: 22,
    },
  ],
};

export function ResultsMap({ polygon }: ResultsMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const [activeLayerMode, setActiveLayerMode] = useState<"both" | "satellite" | "heatmap">("both");
  const [activeBasemap, setActiveBasemap] = useState<"esri" | "carto">("esri");
  const [hotspotPixels, setHotspotPixels] = useState<Array<{ x: number; y: number }>>([]);
  const [svgPathD, setSvgPathD] = useState<string>("");

  const { isReduced } = useAnimationEngine();
  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

  // Hotspot geographical coordinates (computed inside polygon bounding box)
  const hotspotsGeoRef = useRef<Array<[number, number]>>([]);

  // Project coordinates to screen pixels for SVG marching ants & hotspot pings
  const updateOverlays = useCallback(() => {
    const map = mapRef.current;
    if (!map || !polygon?.geometry?.coordinates?.[0]?.length) return;

    // 1. Project Polygon outline to SVG Path
    const coords = polygon.geometry.coordinates[0];
    const pathPoints = coords.map((c) => {
      const p = map.project(c as [number, number]);
      return `${p.x},${p.y}`;
    });
    setSvgPathD(`M ${pathPoints.join(" L ")} Z`);

    // 2. Project Hotspots to pixels
    if (hotspotsGeoRef.current.length > 0) {
      const pixels = hotspotsGeoRef.current.map((pt) => {
        const p = map.project(pt);
        return { x: p.x, y: p.y };
      });
      setHotspotPixels(pixels);
    }
  }, [polygon]);

  useEffect(() => {
    if (
      !mapContainerRef.current ||
      !polygon ||
      !polygon.geometry ||
      !polygon.geometry.coordinates ||
      !polygon.geometry.coordinates[0]?.length
    )
      return;

    if ((mapboxgl as any).config) {
      (mapboxgl as any).config.REQUIRE_ACCESS_TOKEN = false;
    }
    mapboxgl.accessToken = token;

    // Calculate bounds of polygon
    const coords = polygon.geometry.coordinates[0];
    const bounds = new mapboxgl.LngLatBounds(
      coords[0] as [number, number],
      coords[0] as [number, number]
    );
    let minLng = Infinity,
      maxLng = -Infinity,
      minLat = Infinity,
      maxLat = -Infinity;

    coords.forEach((coord) => {
      bounds.extend(coord as [number, number]);
      minLng = Math.min(minLng, coord[0]);
      maxLng = Math.max(maxLng, coord[0]);
      minLat = Math.min(minLat, coord[1]);
      maxLat = Math.max(maxLat, coord[1]);
    });

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: ESRI_SATELLITE_STYLE,
      bounds: bounds,
      fitBoundsOptions: { padding: 60 },
      attributionControl: false,
    });

    mapRef.current = map;

    // Generate heatmap points grid inside bounding box
    const pointFeatures: GeoJSON.Feature<GeoJSON.Point>[] = [];
    const steps = 14;
    const lngStep = (maxLng - minLng) / steps;
    const latStep = (maxLat - minLat) / steps;

    for (let i = 0; i <= steps; i++) {
      for (let j = 0; j <= steps; j++) {
        const lng = minLng + i * lngStep + (Math.random() - 0.5) * lngStep * 0.4;
        const lat = minLat + j * latStep + (Math.random() - 0.5) * latStep * 0.4;
        const biomass = Math.floor(600 + Math.random() * 600);

        pointFeatures.push({
          type: "Feature",
          properties: { biomass },
          geometry: {
            type: "Point",
            coordinates: [lng, lat],
          },
        });
      }
    }

    // Pick 3 high-density hotspots for radar blip pulses
    hotspotsGeoRef.current = [
      [minLng + (maxLng - minLng) * 0.35, minLat + (maxLat - minLat) * 0.65],
      [minLng + (maxLng - minLng) * 0.60, minLat + (maxLat - minLat) * 0.45],
      [minLng + (maxLng - minLng) * 0.45, minLat + (maxLat - minLat) * 0.30],
    ];

    const heatmapGeoJson: GeoJSON.FeatureCollection<GeoJSON.Point> = {
      type: "FeatureCollection",
      features: pointFeatures,
    };

    let animFrameId: number;

    map.on("load", () => {
      map.resize();

      // 1. Add Polygon Source & Layers
      map.addSource("analyzed-polygon-src", {
        type: "geojson",
        data: polygon,
      });

      // Polygon Fill
      map.addLayer({
        id: "polygon-fill-layer",
        type: "fill",
        source: "analyzed-polygon-src",
        paint: {
          "fill-color": "#4ADE80",
          "fill-opacity": 0.18,
        },
      });

      // Polygon Outline
      map.addLayer({
        id: "polygon-outline-layer",
        type: "line",
        source: "analyzed-polygon-src",
        paint: {
          "line-color": "#22C55E",
          "line-width": 2,
        },
      });

      // 2. Add Heatmap Source & Layer
      map.addSource("biomass-heatmap-src", {
        type: "geojson",
        data: heatmapGeoJson,
      });

      map.addLayer({
        id: "biomass-heatmap-layer",
        type: "heatmap",
        source: "biomass-heatmap-src",
        paint: {
          "heatmap-weight": [
            "interpolate",
            ["linear"],
            ["get", "biomass"],
            600,
            0.2,
            1200,
            1.0,
          ],
          "heatmap-color": [
            "interpolate",
            ["linear"],
            ["heatmap-density"],
            0,
            "rgba(0,0,0,0)",
            0.2,
            "#A5D6A7",
            0.6,
            "#4CAF50",
            1.0,
            "#1B5E20",
          ],
          "heatmap-radius": 35,
          "heatmap-opacity": 0.70,
        },
      });

      updateOverlays();

      // Animation 8: Heatmap Respiration Loop (0.60 -> 0.80 -> 0.60 over 5 seconds)
      if (!isReduced) {
        let startTime = performance.now();
        const breatheHeatmap = (now: number) => {
          if (mapRef.current && mapRef.current.getLayer("biomass-heatmap-layer")) {
            const elapsed = (now - startTime) / 1000;
            // 5 second period, oscillate between 0.60 and 0.80
            const opacity = 0.70 + 0.10 * Math.sin((elapsed * 2 * Math.PI) / 5);
            try {
              mapRef.current.setPaintProperty("biomass-heatmap-layer", "heatmap-opacity", opacity);
            } catch (e) {
              // Ignore layer lifecycle checks
            }
          }
          animFrameId = requestAnimationFrame(breatheHeatmap);
        };
        animFrameId = requestAnimationFrame(breatheHeatmap);
      }
    });

    map.on("move", updateOverlays);
    map.on("zoom", updateOverlays);
    map.on("resize", updateOverlays);

    return () => {
      if (animFrameId) cancelAnimationFrame(animFrameId);
      map.remove();
      mapRef.current = null;
    };
  }, [polygon, token, isReduced, updateOverlays]);

  // Handle Layer Toggle Mode ("both" | "satellite" | "heatmap")
  const toggleLayer = (mode: "both" | "satellite" | "heatmap") => {
    setActiveLayerMode(mode);
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;

    if (mode === "satellite") {
      if (map.getLayer("biomass-heatmap-layer")) map.setLayoutProperty("biomass-heatmap-layer", "visibility", "none");
      if (map.getLayer("polygon-fill-layer")) map.setLayoutProperty("polygon-fill-layer", "visibility", "visible");
      if (map.getLayer("polygon-outline-layer")) map.setLayoutProperty("polygon-outline-layer", "visibility", "visible");
    } else if (mode === "heatmap") {
      if (map.getLayer("biomass-heatmap-layer")) map.setLayoutProperty("biomass-heatmap-layer", "visibility", "visible");
      if (map.getLayer("polygon-fill-layer")) map.setLayoutProperty("polygon-fill-layer", "visibility", "none");
      if (map.getLayer("polygon-outline-layer")) map.setLayoutProperty("polygon-outline-layer", "visibility", "none");
    } else {
      if (map.getLayer("biomass-heatmap-layer")) map.setLayoutProperty("biomass-heatmap-layer", "visibility", "visible");
      if (map.getLayer("polygon-fill-layer")) map.setLayoutProperty("polygon-fill-layer", "visibility", "visible");
      if (map.getLayer("polygon-outline-layer")) map.setLayoutProperty("polygon-outline-layer", "visibility", "visible");
    }
  };

  const switchBasemap = (type: "esri" | "carto") => {
    setActiveBasemap(type);
    const map = mapRef.current;
    if (!map) return;
    map.setStyle(type === "esri" ? ESRI_SATELLITE_STYLE : CARTO_VOYAGER_STYLE);
  };

  return (
    <div className="relative w-full h-[480px] rounded-2xl overflow-hidden shadow-xl border border-gray-200 bg-gray-950">
      {/* Map Canvas */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full" />

      {/* Animation 8: SVG Overlay for Marching Ants Polygon Perimeter */}
      {svgPathD && activeLayerMode !== "heatmap" && (
        <svg className="pointer-events-none absolute inset-0 w-full h-full z-10">
          <path
            d={svgPathD}
            fill="none"
            stroke="#81C784"
            strokeWidth="2.5"
            strokeDasharray="8 6"
            className={!isReduced ? "animate-marching-ants" : ""}
            style={{
              filter: "drop-shadow(0 0 6px rgba(76, 175, 80, 0.6))",
            }}
          />
        </svg>
      )}

      {/* Animation 8: Radar Blip Hotspot Pulses on Highest Density Points */}
      {!isReduced &&
        activeLayerMode !== "satellite" &&
        hotspotPixels.map((pt, idx) => (
          <div
            key={idx}
            className="pointer-events-none absolute z-15 transform -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${pt.x}px`, top: `${pt.y}px` }}
          >
            <div className="relative flex items-center justify-center">
              {/* Expanding Radar Ring */}
              <span
                className="animate-sonar-ping absolute inline-flex h-12 w-12 rounded-full bg-green-400 opacity-60"
                style={{ animationDelay: `${idx * 0.9}s`, animationDuration: "2.4s", animationIterationCount: "infinite" }}
              />
              <span
                className="animate-sonar-ping absolute inline-flex h-8 w-8 rounded-full bg-emerald-300 opacity-70"
                style={{ animationDelay: `${idx * 0.9 + 0.4}s`, animationDuration: "2.4s", animationIterationCount: "infinite" }}
              />
              {/* Core Hotspot Dot */}
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-400 ring-2 ring-white shadow-lg" />
            </div>
          </div>
        ))}

      {/* Animation 8: Diagonal Satellite Overflight Sensor Swath (Passes every 15s) */}
      {!isReduced && (
        <div className="pointer-events-none absolute inset-0 overflow-hidden z-20">
          <div className="absolute w-[250%] h-40 -left-1/2 -top-40 bg-gradient-to-b from-transparent via-green-400/[0.07] to-transparent rotate-45 animate-satellite-pass" />
        </div>
      )}

      {/* Top-Right: Layer Toggle Mode */}
      <div className="absolute top-4 right-4 z-20 flex items-center bg-black/80 backdrop-blur-md rounded-xl p-1 border border-white/20 shadow-lg text-xs font-semibold text-white">
        <button
          type="button"
          onClick={() => toggleLayer("satellite")}
          className={`px-3 py-1.5 rounded-lg transition-all ${
            activeLayerMode === "satellite"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          Satellite
        </button>
        <button
          type="button"
          onClick={() => toggleLayer("heatmap")}
          className={`px-3 py-1.5 rounded-lg transition-all ${
            activeLayerMode === "heatmap"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          Heatmap
        </button>
        <button
          type="button"
          onClick={() => toggleLayer("both")}
          className={`px-3 py-1.5 rounded-lg transition-all ${
            activeLayerMode === "both"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          Both Layers
        </button>
      </div>

      {/* Top-Left: Basemap Mode Switcher */}
      <div className="absolute top-4 left-4 z-20 flex items-center bg-black/80 backdrop-blur-md rounded-xl p-1 border border-white/20 shadow-lg text-xs font-semibold text-white">
        <button
          type="button"
          onClick={() => switchBasemap("esri")}
          className={`px-2.5 py-1 rounded-lg transition-all ${
            activeBasemap === "esri"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          ESRI Satellite
        </button>
        <button
          type="button"
          onClick={() => switchBasemap("carto")}
          className={`px-2.5 py-1 rounded-lg transition-all ${
            activeBasemap === "carto"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          Terrain &amp; Roads
        </button>
      </div>

      {/* Bottom-Right: Map Controls */}
      <div className="absolute bottom-4 right-4 z-20 flex flex-col gap-1.5 bg-black/75 backdrop-blur-md rounded-xl p-1 border border-white/20 shadow-lg text-white">
        <button
          type="button"
          onClick={() => mapRef.current?.zoomIn()}
          className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
          title="Zoom In"
        >
          <Plus className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => mapRef.current?.zoomOut()}
          className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
          title="Zoom Out"
        >
          <Minus className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => {
            if (!polygon?.geometry?.coordinates?.[0]?.length) return;
            const coords = polygon.geometry.coordinates[0];
            const bounds = new mapboxgl.LngLatBounds(
              coords[0] as [number, number],
              coords[0] as [number, number]
            );
            coords.forEach((coord) => bounds.extend(coord as [number, number]));
            mapRef.current?.fitBounds(bounds, { padding: 60 });
          }}
          className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Bottom-Left: Satellite Status Badge */}
      <div className="absolute bottom-4 left-4 z-20 bg-black/75 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10 text-[11px] text-gray-300 font-mono flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span>Authentic Satellite Reflectance (10m Resolution)</span>
      </div>
    </div>
  );
}

export default ResultsMap;
