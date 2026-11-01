"use client";

import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import turfArea from "@turf/area";
import { useAnalysis } from "@/context/AnalysisContext";
import { PolygonData } from "@/lib/types";
import { FOREST_DIRECTORY, ForestLocation } from "@/lib/forest-directory";
import {
  Search,
  Plus,
  Minus,
  RotateCcw,
  Sparkles,
  MapPin,
  Trash2,
  Pentagon,
  Globe2,
  BookOpen,
  Crosshair,
  Check,
  ChevronDown,
  X,
} from "lucide-react";

// Real Authentic Global Satellite Style (ESRI World Imagery - Free & Unmetered)
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

const customDrawStyles = [
  // ACTIVE (being drawn)
  {
    id: "gl-draw-polygon-fill-active",
    type: "fill",
    filter: ["all", ["==", "$type", "Polygon"], ["!=", "mode", "static"]],
    paint: {
      "fill-color": "#22C55E",
      "fill-opacity": 0.25,
    },
  },
  {
    id: "gl-draw-polygon-stroke-active",
    type: "line",
    filter: ["all", ["==", "$type", "Polygon"], ["!=", "mode", "static"]],
    layout: {
      "line-cap": "round",
      "line-join": "round",
    },
    paint: {
      "line-color": "#15803D",
      "line-width": 2.5,
      "line-opacity": 0.9,
    },
  },
  // ACTIVE LINE (during polygon draw before closing)
  {
    id: "gl-draw-line-active",
    type: "line",
    filter: ["all", ["==", "$type", "LineString"], ["!=", "mode", "static"]],
    layout: {
      "line-cap": "round",
      "line-join": "round",
    },
    paint: {
      "line-color": "#15803D",
      "line-width": 2.5,
      "line-dasharray": [0.2, 2],
    },
  },
  // INACTIVE (static/saved)
  {
    id: "gl-draw-polygon-fill-static",
    type: "fill",
    filter: ["all", ["==", "$type", "Polygon"], ["==", "mode", "static"]],
    paint: {
      "fill-color": "#22C55E",
      "fill-opacity": 0.25,
    },
  },
  {
    id: "gl-draw-polygon-stroke-static",
    type: "line",
    filter: ["all", ["==", "$type", "Polygon"], ["==", "mode", "static"]],
    layout: {
      "line-cap": "round",
      "line-join": "round",
    },
    paint: {
      "line-color": "#15803D",
      "line-width": 2.5,
      "line-opacity": 0.9,
    },
  },
  // Vertex points
  {
    id: "gl-draw-polygon-and-line-vertex-active",
    type: "circle",
    filter: [
      "all",
      ["==", "meta", "vertex"],
      ["==", "$type", "Point"],
      ["!=", "mode", "static"],
    ],
    paint: {
      "circle-radius": 6,
      "circle-color": "#FFFFFF",
      "circle-stroke-color": "#15803D",
      "circle-stroke-width": 2,
    },
  },
  // Active points (during drawing)
  {
    id: "gl-draw-point-active",
    type: "circle",
    filter: ["all", ["==", "$type", "Point"], ["!=", "mode", "static"]],
    paint: {
      "circle-radius": 6,
      "circle-color": "#FFFFFF",
      "circle-stroke-color": "#15803D",
      "circle-stroke-width": 2,
    },
  },
  // Midpoints
  {
    id: "gl-draw-polygon-midpoint",
    type: "circle",
    filter: ["all", ["==", "meta", "midpoint"], ["==", "$type", "Point"]],
    paint: {
      "circle-radius": 4,
      "circle-color": "#FFFFFF",
      "circle-stroke-color": "#22C55E",
      "circle-stroke-width": 2,
    },
  },
];

export function MapView() {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const drawRef = useRef<MapboxDraw | null>(null);

  const { state, dispatch, runAnalysis } = useAnalysis();

  const [activeBasemap, setActiveBasemap] = useState<"esri" | "mapbox">("esri");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDirectoryOpen, setIsDirectoryOpen] = useState(false);
  const [directoryTab, setDirectoryTab] = useState<"india" | "global">("india");
  const [badgePos, setBadgePos] = useState<{ x: number; y: number } | null>(null);
  const [isDrawingMode, setIsDrawingMode] = useState(false);

  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || "";

  // Filter indexed forests matching search query
  const autocompleteResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    const q = searchQuery.toLowerCase().trim();
    return FOREST_DIRECTORY.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        f.stateOrRegion.toLowerCase().includes(q) ||
        f.forest_type.toLowerCase().includes(q) ||
        f.country.toLowerCase().includes(q)
    ).slice(0, 6);
  }, [searchQuery]);

  // Calculate centroid of polygon for badge positioning
  const updateCentroidPosition = useCallback((polygon: PolygonData) => {
    if (!mapRef.current || !polygon || !polygon.geometry) return;
    try {
      const ring = polygon.geometry.coordinates[0];
      if (!ring || ring.length === 0) return;
      let sumLng = 0;
      let sumLat = 0;
      for (const pt of ring) {
        sumLng += pt[0];
        sumLat += pt[1];
      }
      const centerLng = sumLng / ring.length;
      const centerLat = sumLat / ring.length;
      const point = mapRef.current.project([centerLng, centerLat]);
      setBadgePos({ x: point.x, y: point.y });
    } catch {
      setBadgePos(null);
    }
  }, []);

  // Update badge on map move
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const onMove = () => {
      if (state.polygon) {
        updateCentroidPosition(state.polygon);
      }
    };

    map.on("move", onMove);
    return () => {
      map.off("move", onMove);
    };
  }, [state.polygon, updateCentroidPosition]);

  // Switch basemap layer
  const switchBasemap = useCallback((type: "esri" | "mapbox") => {
    setActiveBasemap(type);
    const map = mapRef.current;
    if (!map) return;

    if (type === "esri") {
      map.setStyle(ESRI_SATELLITE_STYLE);
    } else {
      map.setStyle("mapbox://styles/mapbox/satellite-v9");
    }
  }, []);

  // Helper: Apply a selected forest and auto-create boundary
  const selectForestLocation = useCallback(
    (forest: ForestLocation) => {
      if (!mapRef.current || !drawRef.current) return;

      const [lng, lat] = forest.coords;

      // 1. Smoothly fly satellite camera to coordinates
      mapRef.current.flyTo({
        center: [lng, lat],
        zoom: forest.zoom,
        essential: true,
      });

      // 2. Generate a valid, clean sample conservation polygon around the forest canopy
      const delta = forest.deltaDeg || 0.04;
      const polygonFeature: GeoJSON.Feature<GeoJSON.Polygon> = {
        type: "Feature",
        properties: {
          name: forest.name,
          ecoregion: forest.ecoregion,
          forest_type: forest.forest_type,
        },
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [lng - delta, lat - delta],
              [lng + delta, lat - delta],
              [lng + delta, lat + delta],
              [lng - delta, lat + delta],
              [lng - delta, lat - delta],
            ],
          ],
        },
      };

      // 3. Clear old polygon & draw new one
      drawRef.current.deleteAll();
      drawRef.current.add(polygonFeature);

      // 4. Calculate exact area in hectares with @turf/area
      const areaSqM = turfArea(polygonFeature);
      const hectares = Math.round((areaSqM / 10000) * 10) / 10;

      dispatch({ type: "SET_POLYGON", payload: polygonFeature });
      dispatch({ type: "SET_AREA", payload: hectares });

      setIsDropdownOpen(false);
      setIsDirectoryOpen(false);
      setSearchQuery(forest.name);

      setTimeout(() => updateCentroidPosition(polygonFeature), 350);
    },
    [dispatch, updateCentroidPosition]
  );

  // Helper: Auto-Select Area at Current Map Center
  const autoSelectAreaAtCenter = useCallback(() => {
    if (!mapRef.current || !drawRef.current) return;

    const center = mapRef.current.getCenter();
    const zoom = mapRef.current.getZoom();
    const delta = Math.max(0.015, 0.04 * Math.pow(2, 10 - zoom));

    const polygonFeature: GeoJSON.Feature<GeoJSON.Polygon> = {
      type: "Feature",
      properties: { name: `Selected Forest Plot (${center.lat.toFixed(2)}°, ${center.lng.toFixed(2)}°)` },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [center.lng - delta, center.lat - delta],
            [center.lng + delta, center.lat - delta],
            [center.lng + delta, center.lat + delta],
            [center.lng - delta, center.lat + delta],
            [center.lng - delta, center.lat - delta],
          ],
        ],
      },
    };

    drawRef.current.deleteAll();
    drawRef.current.add(polygonFeature);

    const areaSqM = turfArea(polygonFeature);
    const hectares = Math.round((areaSqM / 10000) * 10) / 10;

    dispatch({ type: "SET_POLYGON", payload: polygonFeature });
    dispatch({ type: "SET_AREA", payload: hectares });
    setTimeout(() => updateCentroidPosition(polygonFeature), 200);
  }, [dispatch, updateCentroidPosition]);

  // Toggle Custom Polygon Drawing Mode
  const toggleDrawPolygon = useCallback(() => {
    if (!drawRef.current || !mapRef.current) return;

    if (isDrawingMode) {
      // Exit drawing mode
      drawRef.current.changeMode("simple_select");
      setIsDrawingMode(false);
      mapRef.current.doubleClickZoom.enable();
      if (mapRef.current.getCanvas()) {
        mapRef.current.getCanvas().style.cursor = "";
      }
    } else {
      // Clear previous polygon and start fresh drawing
      drawRef.current.deleteAll();
      dispatch({ type: "CLEAR_POLYGON" });
      setBadgePos(null);

      drawRef.current.changeMode("draw_polygon");
      setIsDrawingMode(true);
      mapRef.current.doubleClickZoom.disable();
      if (mapRef.current.getCanvas()) {
        mapRef.current.getCanvas().style.cursor = "crosshair";
      }
    }
  }, [isDrawingMode, dispatch]);

  // Cancel drawing on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isDrawingMode && drawRef.current) {
        drawRef.current.changeMode("simple_select");
        setIsDrawingMode(false);
        if (mapRef.current) {
          mapRef.current.doubleClickZoom.enable();
          if (mapRef.current.getCanvas()) {
            mapRef.current.getCanvas().style.cursor = "";
          }
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isDrawingMode]);

  // Initialize Mapbox map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    mapboxgl.accessToken = token;

    // Default map starts centered over Western Ghats, India!
    const defaultCenter: [number, number] = [76.4405, 11.1389];

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: ESRI_SATELLITE_STYLE,
      center: defaultCenter,
      zoom: 10,
      attributionControl: false,
    });

    map.addControl(new mapboxgl.AttributionControl({ compact: true }), "bottom-right");

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: {}, // Don't render default Mapbox control buttons; our custom toolbar buttons control drawing without overlap
      styles: customDrawStyles,
    });

    map.addControl(draw as unknown as mapboxgl.IControl, "top-left");

    drawRef.current = draw;
    mapRef.current = map;

    // Auto-fallback to ESRI Satellite if Mapbox style is blocked or rate-limited
    map.on("error", (e: any) => {
      if (e?.error?.status === 429 || e?.error?.message?.includes("Too Many Requests")) {
        console.warn("Mapbox rate limit hit; fallback active.");
        map.setStyle(ESRI_SATELLITE_STYLE);
        setActiveBasemap("esri");
      }
    });

    const handleCreateOrUpdate = (e: { features: GeoJSON.Feature[] }) => {
      const feature = e.features[0];
      if (!feature || feature.geometry.type !== "Polygon") return;

      setIsDrawingMode(false);
      map.doubleClickZoom.enable();
      if (map.getCanvas()) {
        map.getCanvas().style.cursor = "";
      }

      const polygon = feature as PolygonData;
      const areaSqMeters = turfArea(polygon);
      const areaHectares = Math.round((areaSqMeters / 10000) * 10) / 10;

      dispatch({ type: "SET_POLYGON", payload: polygon });
      dispatch({ type: "SET_AREA", payload: areaHectares });
      updateCentroidPosition(polygon);
    };

    const handleDelete = () => {
      setIsDrawingMode(false);
      map.doubleClickZoom.enable();
      if (map.getCanvas()) {
        map.getCanvas().style.cursor = "";
      }
      dispatch({ type: "CLEAR_POLYGON" });
      setBadgePos(null);
    };

    const handleModeChange = (e: { mode: string }) => {
      const drawing = e.mode === "draw_polygon";
      setIsDrawingMode(drawing);
      if (map.getCanvas()) {
        map.getCanvas().style.cursor = drawing ? "crosshair" : "";
      }
      if (drawing) {
        map.doubleClickZoom.disable();
      } else {
        map.doubleClickZoom.enable();
      }
    };

    map.on("draw.create" as any, handleCreateOrUpdate);
    map.on("draw.update" as any, handleCreateOrUpdate);
    map.on("draw.delete" as any, handleDelete);
    map.on("draw.modechange" as any, handleModeChange);

    return () => {
      map.remove();
      mapRef.current = null;
      drawRef.current = null;
    };
  }, [token, dispatch, updateCentroidPosition]);

  // Global search using Photon OpenStreetMap API (Free, unlimited global geocoding for India & World)
  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || !mapRef.current) return;

    // Check if query matches indexed forest first
    const matched = FOREST_DIRECTORY.find((f) =>
      f.name.toLowerCase().includes(searchQuery.toLowerCase().trim())
    );
    if (matched) {
      selectForestLocation(matched);
      return;
    }

    setIsSearching(true);
    setIsDropdownOpen(false);

    try {
      // Query global Photon Geocoder
      const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(searchQuery)}&limit=1`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.features && data.features.length > 0) {
        const feat = data.features[0];
        const [lng, lat] = feat.geometry.coordinates;
        mapRef.current.flyTo({ center: [lng, lat], zoom: 11, essential: true });

        // Auto-select a 1,500 ha plot around found coordinates
        const delta = 0.035;
        const polygonFeature: GeoJSON.Feature<GeoJSON.Polygon> = {
          type: "Feature",
          properties: { name: feat.properties.name || searchQuery },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [lng - delta, lat - delta],
                [lng + delta, lat - delta],
                [lng + delta, lat + delta],
                [lng - delta, lat + delta],
                [lng - delta, lat - delta],
              ],
            ],
          },
        };

        if (drawRef.current) {
          drawRef.current.deleteAll();
          drawRef.current.add(polygonFeature);
        }

        const areaSqM = turfArea(polygonFeature);
        const ha = Math.round((areaSqM / 10000) * 10) / 10;
        dispatch({ type: "SET_POLYGON", payload: polygonFeature });
        dispatch({ type: "SET_AREA", payload: ha });
        setTimeout(() => updateCentroidPosition(polygonFeature), 300);
      } else {
        alert(`Location "${searchQuery}" not found. Try searching for specific forests like "Sundarbans", "Corbett", "Silent Valley", or "Amazon".`);
      }
    } catch {
      alert("Search connection failed. Please select from the Forest Directory button above.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className={`relative w-full h-full min-h-[400px] overflow-hidden bg-gray-950 ${isDrawingMode ? "drawing-mode" : ""}`}>
      {/* Active Drawing Guide Banner */}
      {isDrawingMode && (
        <div
          className="absolute top-20 left-1/2 -translate-x-1/2 z-30 bg-gray-900/95 text-white backdrop-blur-md px-4 py-2 rounded-2xl shadow-2xl border border-amber-400/80 text-xs font-medium flex items-center gap-3 animate-in fade-in slide-in-from-top-2"
          onMouseDown={(e) => e.stopPropagation()}
          onClick={(e) => e.stopPropagation()}
        >
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
          <span>Click map to place boundary points • Double-click or click first point to close shape</span>
          <button
            type="button"
            onClick={toggleDrawPolygon}
            className="px-2 py-0.5 rounded-lg bg-white/10 hover:bg-white/20 text-white font-bold text-[11px] border border-white/20 transition-colors"
          >
            Cancel (Esc)
          </button>
        </div>
      )}
      {/* Mapbox Canvas */}
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full" />

      {/* Top Center: Search Bar & Forest Index Explorer */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center gap-2 max-w-xl w-full px-4">
        <div className="relative w-full">
          <form onSubmit={handleSearchSubmit} className="relative w-full shadow-2xl">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsDropdownOpen(true);
              }}
              onFocus={() => setIsDropdownOpen(true)}
              placeholder="Search any forest in India or World (e.g. Western Ghats, Sundarbans, Corbett, Amazon)..."
              className="w-full pl-10 pr-32 py-3 text-xs sm:text-sm bg-white/95 backdrop-blur-md rounded-2xl border border-gray-200 text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-600 shadow-xl"
            />
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-gray-400" />

            <div className="absolute right-1.5 top-1.5 flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => setIsDirectoryOpen(true)}
                className="px-2.5 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 text-xs font-semibold rounded-xl border border-green-200 transition-colors flex items-center gap-1"
                title="Browse Forest Directory"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Directory</span>
              </button>

              <button
                type="submit"
                disabled={isSearching}
                className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
              >
                {isSearching ? "Searching..." : "Fly"}
              </button>
            </div>
          </form>

          {/* Autocomplete Dropdown List */}
          {isDropdownOpen && autocompleteResults.length > 0 && (
            <div
              className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-40 max-h-72 overflow-y-auto animate-in fade-in zoom-in-95 duration-150"
              onMouseLeave={() => setIsDropdownOpen(false)}
            >
              <div className="p-2 border-b border-gray-100 text-[10px] font-bold uppercase tracking-wider text-gray-400 bg-gray-50 flex items-center justify-between">
                <span>Matching Forests</span>
                <span className="text-gray-400">Click to Fly &amp; Select Area</span>
              </div>
              {autocompleteResults.map((forest) => (
                <button
                  key={forest.id}
                  type="button"
                  onClick={() => selectForestLocation(forest)}
                  className="w-full px-4 py-2.5 text-left hover:bg-green-50 transition-colors flex items-center justify-between gap-3 border-b border-gray-50 last:border-0"
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <span className="text-base">{forest.country === "India" ? "🇮🇳" : "🌍"}</span>
                    <div className="truncate">
                      <p className="text-xs font-bold text-gray-900 truncate">{forest.name}</p>
                      <p className="text-[11px] text-gray-500 truncate">{forest.stateOrRegion} • {forest.forest_type}</p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono text-green-700 bg-green-100/70 px-2 py-0.5 rounded-full shrink-0">
                    {forest.sampleAreaHa.toLocaleString()} ha
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Quick Jump Chips */}
        <div className="flex flex-wrap gap-1.5 justify-center">
          <button
            type="button"
            onClick={() => selectForestLocation(FOREST_DIRECTORY[0])} // Silent Valley
            className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-900/80 text-white hover:bg-black backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 shadow-xs"
          >
            <span>🇮🇳 Western Ghats</span>
          </button>
          <button
            type="button"
            onClick={() => selectForestLocation(FOREST_DIRECTORY[1])} // Sundarbans
            className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-900/80 text-white hover:bg-black backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 shadow-xs"
          >
            <span>🇮🇳 Sundarbans</span>
          </button>
          <button
            type="button"
            onClick={() => selectForestLocation(FOREST_DIRECTORY[2])} // Corbett
            className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-900/80 text-white hover:bg-black backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 shadow-xs"
          >
            <span>🇮🇳 Jim Corbett</span>
          </button>
          <button
            type="button"
            onClick={() => selectForestLocation(FOREST_DIRECTORY[3])} // Kaziranga
            className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-900/80 text-white hover:bg-black backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 shadow-xs"
          >
            <span>🇮🇳 Kaziranga</span>
          </button>
          <button
            type="button"
            onClick={() => selectForestLocation(FOREST_DIRECTORY[13])} // Amazon
            className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-gray-900/80 text-white hover:bg-black backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 shadow-xs"
          >
            <span>🌍 Amazon Basin</span>
          </button>
        </div>
      </div>

      {/* Forest Directory Modal Dialog */}
      {isDirectoryOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-gray-100 flex flex-col max-h-[85vh] overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-gray-100">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-green-50 text-green-700">
                  <BookOpen className="w-5 h-5 text-green-700" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    Forest Inventory Directory
                  </h3>
                  <p className="text-xs text-gray-500">
                    Select any indexed forest tract in India or around the world to fly &amp; select area
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsDirectoryOpen(false)}
                className="p-1.5 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Country Category Tabs */}
            <div className="flex items-center gap-2 my-4 p-1 bg-gray-100 rounded-xl">
              <button
                type="button"
                onClick={() => setDirectoryTab("india")}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                  directoryTab === "india"
                    ? "bg-white text-gray-900 shadow-xs"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                <span>🇮🇳 India Forests &amp; Reserves (13)</span>
              </button>
              <button
                type="button"
                onClick={() => setDirectoryTab("global")}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 ${
                  directoryTab === "global"
                    ? "bg-white text-gray-900 shadow-xs"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                <span>🌍 World Forests (8)</span>
              </button>
            </div>

            {/* Forest Listings Grid */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {FOREST_DIRECTORY.filter((f) => f.category === directoryTab).map((forest) => (
                <div
                  key={forest.id}
                  onClick={() => selectForestLocation(forest)}
                  className="p-3.5 rounded-2xl border border-gray-200 hover:border-green-500 hover:bg-green-50/60 transition-all cursor-pointer flex items-center justify-between gap-4 group"
                >
                  <div className="flex items-start gap-3 truncate">
                    <div className="p-2 rounded-xl bg-gray-50 group-hover:bg-green-100 text-gray-700 group-hover:text-green-800 transition-colors shrink-0">
                      <MapPin className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <h4 className="text-sm font-bold text-gray-900 group-hover:text-green-800 truncate">
                        {forest.name}
                      </h4>
                      <p className="text-xs text-gray-500 mt-0.5 truncate">
                        {forest.stateOrRegion} • <span className="font-medium text-gray-600">{forest.forest_type}</span>
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="font-mono text-xs font-bold text-green-700 bg-green-100 px-2.5 py-1 rounded-full block mb-1">
                      {forest.sampleAreaHa.toLocaleString()} ha
                    </span>
                    <span className="text-[10px] text-gray-400 group-hover:text-green-600 font-semibold flex items-center gap-1 justify-end">
                      Fly &amp; Select →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Left Toolbar: Drawing & Auto-Select Area */}
      <div
        className="absolute top-28 left-4 z-20 flex flex-col gap-2.5"
        onMouseDown={(e) => e.stopPropagation()}
        onClick={(e) => e.stopPropagation()}
        onDoubleClick={(e) => e.stopPropagation()}
      >
        {/* Draw Custom Polygon Tool */}
        <button
          type="button"
          onClick={toggleDrawPolygon}
          className={`p-3 rounded-2xl shadow-xl border transition-all flex items-center gap-2 text-xs font-bold ${
            isDrawingMode
              ? "bg-amber-500 text-white border-amber-600 hover:bg-amber-600 ring-2 ring-amber-300"
              : "bg-white/95 text-gray-800 hover:text-green-700 hover:bg-green-50 border-gray-200"
          }`}
          title={isDrawingMode ? "Cancel Custom Drawing (Esc)" : "Draw Custom Forest Boundary"}
        >
          {isDrawingMode ? (
            <>
              <X className="w-4 h-4 text-white" />
              <span className="hidden sm:inline">Cancel Drawing</span>
            </>
          ) : (
            <>
              <Pentagon className="w-4 h-4 text-green-600" />
              <span className="hidden sm:inline">Draw Custom Area</span>
            </>
          )}
        </button>

        {/* Auto-Select Area at Center Crosshair */}
        <button
          type="button"
          onClick={autoSelectAreaAtCenter}
          disabled={isDrawingMode}
          className={`p-3 rounded-2xl bg-white/95 text-gray-800 hover:text-green-700 hover:bg-green-50 shadow-xl border border-gray-200 transition-all flex items-center gap-2 text-xs font-bold ${
            isDrawingMode ? "opacity-50 cursor-not-allowed pointer-events-none" : ""
          }`}
          title="Auto-select forest boundary at current map center"
        >
          <Crosshair className="w-4 h-4 text-emerald-600" />
          <span className="hidden sm:inline">Select Area Here</span>
        </button>

        {/* Clear Drawn Polygon */}
        {state.polygon && (
          <button
            type="button"
            onClick={() => {
              drawRef.current?.deleteAll();
              dispatch({ type: "CLEAR_POLYGON" });
              setBadgePos(null);
            }}
            disabled={isDrawingMode}
            className={`p-3 rounded-2xl bg-white/95 text-red-600 hover:bg-red-50 shadow-xl border border-red-200 transition-all flex items-center gap-2 text-xs font-bold ${
              isDrawingMode ? "opacity-50 cursor-not-allowed pointer-events-none" : ""
            }`}
            title="Delete Polygon"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
            <span className="hidden sm:inline">Clear Boundary</span>
          </button>
        )}
      </div>

      {/* Basemap Source Switcher (Bottom-Left) */}
      <div className="absolute bottom-6 left-6 z-20 bg-gray-900/90 text-white backdrop-blur-md px-2 py-1.5 rounded-2xl shadow-2xl border border-white/20 flex items-center gap-1 text-xs">
        <span className="text-[10px] text-gray-400 px-1 font-bold uppercase tracking-wider flex items-center gap-1">
          <Globe2 className="w-3.5 h-3.5 text-green-400" /> Basemap:
        </span>
        <button
          type="button"
          onClick={() => switchBasemap("esri")}
          className={`px-2.5 py-1 rounded-xl text-xs font-semibold transition-all ${
            activeBasemap === "esri"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          ESRI High-Res Satellite
        </button>
        <button
          type="button"
          onClick={() => switchBasemap("mapbox")}
          className={`px-2.5 py-1 rounded-xl text-xs font-semibold transition-all ${
            activeBasemap === "mapbox"
              ? "bg-green-600 text-white shadow-xs"
              : "text-gray-300 hover:text-white"
          }`}
        >
          Mapbox Satellite
        </button>
      </div>

      {/* Zoom Controls (Bottom-Right) */}
      <div className="absolute bottom-6 right-6 z-20 flex flex-col gap-1.5 bg-white/95 backdrop-blur-md rounded-2xl p-1 shadow-2xl border border-gray-200">
        <button
          type="button"
          onClick={() => mapRef.current?.zoomIn()}
          className="p-2 rounded-xl text-gray-700 hover:bg-gray-100 hover:text-green-700 transition-colors"
          title="Zoom In"
        >
          <Plus className="w-4 h-4" />
        </button>
        <div className="w-full h-px bg-gray-200" />
        <button
          type="button"
          onClick={() => mapRef.current?.zoomOut()}
          className="p-2 rounded-xl text-gray-700 hover:bg-gray-100 hover:text-green-700 transition-colors"
          title="Zoom Out"
        >
          <Minus className="w-4 h-4" />
        </button>
        <div className="w-full h-px bg-gray-200" />
        <button
          type="button"
          onClick={() => {
            if (state.polygon) {
              const coords = state.polygon.geometry.coordinates[0];
              const bounds = new mapboxgl.LngLatBounds(
                coords[0] as [number, number],
                coords[0] as [number, number]
              );
              coords.forEach((coord) => bounds.extend(coord as [number, number]));
              mapRef.current?.fitBounds(bounds, { padding: 80 });
            } else {
              mapRef.current?.flyTo({ center: [76.4405, 11.1389], zoom: 10 });
            }
          }}
          className="p-2 rounded-xl text-gray-700 hover:bg-gray-100 hover:text-green-700 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Floating Centroid Area Badge */}
      {badgePos && state.areaHa && (
        <div
          className="absolute z-20 -translate-x-1/2 -translate-y-1/2 pointer-events-none transition-all duration-75"
          style={{ left: badgePos.x, top: badgePos.y }}
        >
          <div className="bg-gray-900/90 text-white backdrop-blur-md px-3.5 py-1.5 rounded-full shadow-2xl border border-green-500/60 font-mono text-xs font-bold flex items-center gap-2 animate-in fade-in zoom-in-75">
            <span className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse" />
            <span>{state.areaHa.toLocaleString()} ha</span>
          </div>
        </div>
      )}

      {/* Floating "Analyze This Area →" Button (Bottom-Center) */}
      {state.polygon && state.areaHa && state.analysisStatus !== "loading" && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 animate-in slide-in-from-bottom-4 duration-300">
          {state.areaHa < 10.0 ? (
            <div className="flex flex-col items-center gap-1.5">
              <button
                type="button"
                onClick={() =>
                  alert(
                    `Selected area is ${state.areaHa} ha. The satellite engine requires at least 10 hectares for statistically verified carbon calculations. Please draw a slightly larger boundary or pick a preset forest.`
                  )
                }
                className="bg-amber-600 hover:bg-amber-700 text-white rounded-full px-6 py-3 font-bold text-xs shadow-2xl transition-all flex items-center gap-2.5 border border-amber-400/50"
              >
                <span>Area Too Small ({state.areaHa} ha)</span>
                <span className="font-mono text-[10px] bg-amber-800 px-2 py-0.5 rounded-full">
                  Min 10 ha
                </span>
              </button>
              <span className="text-[11px] bg-gray-900/90 text-amber-300 px-3 py-1 rounded-full backdrop-blur-sm border border-amber-500/40 font-medium">
                Tip: Expand polygon to &gt;10 ha to run live satellite analysis
              </span>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => runAnalysis()}
              className="bg-green-600 hover:bg-green-700 text-white rounded-full px-8 py-3.5 font-bold text-sm shadow-2xl shadow-green-950/60 hover:-translate-y-0.5 transition-all flex items-center gap-3 border border-green-400/50 group"
            >
              <span>Analyze This Area</span>
              <span className="font-mono text-xs bg-green-800 px-2.5 py-0.5 rounded-full">
                {state.areaHa.toLocaleString()} ha
              </span>
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default MapView;
