"use client";

import React, { useState, useMemo, useEffect } from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { useAuth } from "@/context/AuthContext";
import { mockSavedAnalyses, mockUser } from "@/lib/mock-data";
import { SavedAnalysis } from "@/lib/types";
import { motion, AnimatePresence } from "framer-motion";
import {
  TreePine,
  Plus,
  Search,
  Download,
  ShieldCheck,
  TrendingUp,
  MapPin,
  Layers,
  ArrowUpRight,
  Sparkles,
  BarChart3,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Activity,
  Globe2,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { api, normalizeAnalysisResponse } from "@/lib/api";

export default function DashboardPage() {
  const { user, isAuthenticated, signIn } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [backendItems, setBackendItems] = useState<SavedAnalysis[]>([]);

  // Fetch real analyses from Render backend
  useEffect(() => {
    let isMounted = true;
    api
      .listAnalyses()
      .then((res) => {
        if (!isMounted || !res || !res.analyses) return;
        const mapped: SavedAnalysis[] = res.analyses.map((item: any) => ({
          id: item.analysis_id,
          user_id: "usr_canopy_9981",
          location_name: item.forest_type || "Monitored Forest Plot",
          status: item.status || "complete",
          created_at: item.timestamp || new Date().toISOString(),
          analysis_result: normalizeAnalysisResponse(item),
        }));
        setBackendItems(mapped);
      })
      .catch(() => {
        // Fallback silently to mock analyses when remote API is offline
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const allSavedAnalyses = useMemo(() => {
    const ids = new Set<string>();
    const combined: SavedAnalysis[] = [];
    [...backendItems, ...mockSavedAnalyses].forEach((it) => {
      const itId = it.analysis_result?.analysis_id || it.id;
      if (!ids.has(itId)) {
        ids.add(itId);
        combined.push(it);
      }
    });
    return combined;
  }, [backendItems]);

  const currentUser = user || (isAuthenticated ? mockUser : null);

  // Compute stats across saved analyses
  const stats = useMemo(() => {
    const totalAnalyses = allSavedAnalyses.length;
    let totalHa = 0;
    let totalCo2e = 0;

    allSavedAnalyses.forEach((item) => {
      totalHa += item.analysis_result.area_ha || 0;
      totalCo2e += item.analysis_result.total_co2e || 0;
    });

    return {
      totalAnalyses,
      totalAreaHa: totalHa,
      totalCo2e: totalCo2e,
      activeProjects: Math.max(3, allSavedAnalyses.length),
    };
  }, [allSavedAnalyses]);

  // Filter analyses
  const filteredAnalyses = useMemo(() => {
    return allSavedAnalyses.filter((item) => {
      const matchesSearch =
        item.location_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.analysis_result.forest_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.analysis_result.ecoregion.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesStatus =
        statusFilter === "all" || item.status.toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });
  }, [allSavedAnalyses, searchQuery, statusFilter]);

  return (
    <div className="flex flex-col min-h-screen bg-[#020b04] text-white relative overflow-hidden">
      {/* Living Aerial Forest Ambient Mesh with Cinematic Deep Shadows */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden select-none">
        {/* Spaceborne High-Altitude Aerial Rainforest Canopy Wallpaper */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-85 will-change-transform animate-canopy-breathe"
          style={{ backgroundImage: "url('/images/theme-drone-canopy.jpg')" }}
        />
        {/* Layer 1: Atmospheric Depth Shadow Wash */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#020b04]/80 via-[#020b04]/45 to-[#020b04]/90" />
        {/* Layer 2: Radial Peripheral Shadow Vignette */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,rgba(0,0,0,0.85)_100%)]" />
        {/* Layer 3: Inset Perimeter Deep Shadow */}
        <div className="absolute inset-0 [box-shadow:inset_0_0_180px_rgba(0,0,0,0.92)]" />
        
        {/* Radial emerald light aura & crepuscular rays */}
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[900px] h-[550px] bg-gradient-to-b from-emerald-500/25 via-emerald-600/10 to-transparent blur-3xl rounded-full" />
        <div className="absolute bottom-0 right-0 w-[650px] h-[450px] bg-gradient-to-t from-emerald-600/20 via-green-500/5 to-transparent blur-3xl rounded-full" />
      </div>

      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 space-y-9 relative z-10">
        {/* Unauthenticated notice if not signed in */}
        {!isAuthenticated && (
          <motion.div
            initial={{ opacity: 0, y: -15 }}
            animate={{ opacity: 1, y: 0 }}
            className="crystal-glass-card rounded-3xl p-5 border border-amber-400/30 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl text-white"
          >
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-2xl bg-amber-400/20 text-amber-300 border border-amber-400/30 shadow-inner">
                <AlertTriangle className="w-5 h-5 text-amber-300" />
              </div>
              <div>
                <h4 className="font-bold text-amber-200 text-sm">Demo Research Mode Active</h4>
                <p className="text-xs text-amber-100/80">
                  Sign in or use our one-click researcher credentials to access live satellite computing and PDF MRV export.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                size="sm"
                variant="outline"
                onClick={() => signIn("elena.rostova@canopyai.earth", "password")}
                className="bg-white/10 hover:bg-white/20 border-white/20 text-white rounded-xl backdrop-blur-md"
              >
                Sign In as Dr. Elena
              </Button>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg shadow-emerald-950/50" asChild>
                <Link href="/login">Log In</Link>
              </Button>
            </div>
          </motion.div>
        )}

        {/* Dashboard Welcome Header with Glass Capsule */}
        <div className="crystal-glass-card rounded-3xl p-7 sm:p-9 border border-white/15 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
          {/* Subtle top specular shimmer */}
          <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />

          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 shadow-inner">
                <Globe2 className="w-6 h-6 text-emerald-400 animate-pulse" />
              </div>
              <div>
                <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight flex items-center gap-3">
                  Ecological Portfolio
                  <span className="text-xs font-mono font-bold uppercase tracking-widest text-emerald-300 bg-emerald-500/20 px-3 py-1 rounded-full border border-emerald-400/30 shadow-inner">
                    Active MRV
                  </span>
                </h1>
                <p className="text-xs sm:text-sm text-gray-300 mt-1">
                  Spaceborne forest carbon monitoring for{" "}
                  <strong className="text-emerald-300 font-semibold">
                    {currentUser?.full_name || "Dr. Elena Rostova"}
                  </strong>
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const dataStr =
                  "data:text/json;charset=utf-8," +
                  encodeURIComponent(JSON.stringify(mockSavedAnalyses, null, 2));
                const anchor = document.createElement("a");
                anchor.setAttribute("href", dataStr);
                anchor.setAttribute("download", `canopy-portfolio-export.json`);
                document.body.appendChild(anchor);
                anchor.click();
                anchor.remove();
              }}
              className="gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20 rounded-xl backdrop-blur-md"
            >
              <Download className="w-4 h-4 text-emerald-300" />
              Export Portfolio
            </Button>

            <Button
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-2 rounded-xl shadow-xl shadow-emerald-950/60 border border-emerald-400/40 hover:scale-105 active:scale-95 transition-all"
              asChild
            >
              <Link href="/analyze">
                <Plus className="w-4 h-4" />
                New Forest Analysis
              </Link>
            </Button>
          </div>
        </div>

        {/* 4 Stat Cards Overview with Green Glass Animation */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 [perspective:1000px]">
          {/* Card 1: Total Analyses */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Completed Analyses
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <Layers className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-white font-mono tracking-tight drop-shadow-sm">
                {stats.totalAnalyses}
              </p>
              <div className="flex items-center gap-1.5 text-xs text-emerald-300 font-medium mt-2">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>All plots verified (Tier 3)</span>
              </div>
            </div>
          </motion.div>

          {/* Card 2: Total Area Monitored */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Area Monitored
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <MapPin className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-white font-mono tracking-tight drop-shadow-sm">
                {Math.round(stats.totalAreaHa).toLocaleString("en-US")}
                <span className="text-base font-normal text-emerald-300 ml-1.5 font-sans">ha</span>
              </p>
              <p className="text-xs text-gray-300 mt-2">
                Across Western Ghats, Amazon &amp; Borneo
              </p>
            </div>
          </motion.div>

          {/* Card 3: Total Carbon Stock */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Total CO₂e Stored
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <TreePine className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-emerald-400 font-mono tracking-tight drop-shadow-sm">
                {(stats.totalCo2e / 1000000).toFixed(2)}M
                <span className="text-base font-normal text-gray-300 ml-1.5 font-sans">tCO₂e</span>
              </p>
              <div className="flex items-center gap-1.5 text-xs text-emerald-300 font-medium mt-2">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>+303k tCO₂e / yr sequestration</span>
              </div>
            </div>
          </motion.div>

          {/* Card 4: Estimated Crediting Value */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Annual Est. Revenue
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-amber-400 font-mono tracking-tight drop-shadow-sm">
                $4.55M
                <span className="text-base font-normal text-gray-300 ml-1.5 font-sans">USD</span>
              </p>
              <p className="text-xs text-gray-300 mt-2">
                Based on $15.00 / tCO₂e baseline
              </p>
            </div>
          </motion.div>
        </div>

        {/* Monitored Forest Sites Glass Table */}
        <div className="crystal-glass-card rounded-3xl border border-white/15 shadow-2xl overflow-hidden">
          {/* Table Toolbar */}
          <div className="p-6 border-b border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                Monitored Forest Sites
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              </h2>
              <p className="text-xs text-gray-300 mt-0.5">
                Multi-spectral 10m satellite MRV plots with ongoing optical &amp; radar telemetry
              </p>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              {/* Search Bar */}
              <div className="relative">
                <Input
                  placeholder="Filter by forest name or biome..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 h-10 text-xs w-52 sm:w-64 bg-white/10 border-white/20 text-white placeholder:text-gray-400 rounded-xl focus:ring-2 focus:ring-emerald-400"
                />
                <Search className="w-4 h-4 text-emerald-400 absolute left-3 top-3 pointer-events-none" />
              </div>

              {/* Status Select */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="h-10 px-3.5 rounded-xl border border-white/20 bg-black/40 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 backdrop-blur-md"
              >
                <option value="all" className="bg-gray-900 text-white">All Statuses</option>
                <option value="complete" className="bg-gray-900 text-white">Complete (Audited)</option>
                <option value="processing" className="bg-gray-900 text-white">Processing</option>
              </select>
            </div>
          </div>

          {/* Table */}
          {filteredAnalyses.length === 0 ? (
            <div className="text-center py-20 px-4">
              <TreePine className="w-14 h-14 text-emerald-400/40 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-white">No matching forest plots found</h3>
              <p className="text-xs text-gray-400 max-w-sm mx-auto mt-1 mb-6">
                Try adjusting your search filter or delineate a new boundary in the satellite analyzer.
              </p>
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg" asChild>
                <Link href="/analyze">Start New Analysis</Link>
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-white/5 border-b border-white/10">
                  <TableRow className="border-b border-white/10 hover:bg-transparent">
                    <TableHead className="text-xs font-semibold text-emerald-300">Forest Tract / Biome</TableHead>
                    <TableHead className="text-xs font-semibold text-emerald-300">Ecoregion</TableHead>
                    <TableHead className="text-xs font-semibold text-right text-emerald-300">Area (ha)</TableHead>
                    <TableHead className="text-xs font-semibold text-right text-emerald-300">Biomass Density</TableHead>
                    <TableHead className="text-xs font-semibold text-right text-emerald-300">Total CO₂e</TableHead>
                    <TableHead className="text-xs font-semibold text-center text-emerald-300">Confidence</TableHead>
                    <TableHead className="text-xs font-semibold text-center text-emerald-300">MRV Status</TableHead>
                    <TableHead className="text-xs font-semibold text-right text-emerald-300">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAnalyses.map((item, idx) => {
                    const res = item.analysis_result;
                    const dateFormatted = new Date(item.created_at).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    });

                    return (
                      <TableRow
                        key={item.id}
                        className="border-b border-white/5 hover:bg-white/10 transition-colors group"
                      >
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 shrink-0 group-hover:scale-105 transition-transform">
                              <TreePine className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div>
                              <p className="font-bold text-white text-sm group-hover:text-emerald-300 transition-colors">
                                {item.location_name}
                              </p>
                              <p className="text-[11px] text-gray-400 font-mono">
                                ID: {res.analysis_id} • {dateFormatted}
                              </p>
                            </div>
                          </div>
                        </TableCell>

                        <TableCell className="text-xs text-gray-300 max-w-[200px] truncate">
                          {res.ecoregion}
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs font-semibold text-white">
                          {res.area_ha?.toLocaleString("en-US")} ha
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs text-gray-300">
                          {res.total_biomass_t_per_ha?.toFixed(1)} t/ha
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs font-bold text-emerald-400">
                          {Math.round(res.total_co2e)?.toLocaleString("en-US")} t
                        </TableCell>

                        <TableCell className="text-center">
                          <span className="inline-flex items-center gap-1 font-mono text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-400/30">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                            {Math.round(res.confidence_score)}%
                          </span>
                        </TableCell>

                        <TableCell className="text-center">
                          <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-emerald-300 bg-emerald-500/20 px-3 py-1 rounded-full border border-emerald-400/30 shadow-xs">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            Complete
                          </span>
                        </TableCell>

                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-xs text-emerald-300 hover:text-white hover:bg-emerald-500/20 rounded-xl gap-1"
                            asChild
                          >
                            <Link href={`/results/${res.analysis_id}`}>
                              <span>Audit Dossier</span>
                              <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
                            </Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
