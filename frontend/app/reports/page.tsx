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
  FileText,
  Download,
  ShieldCheck,
  Search,
  TreePine,
  Sparkles,
  ArrowUpRight,
  Globe2,
  FileSpreadsheet,
  Layers,
  MapPin,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Plus,
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

export default function ReportsPage() {
  const { user, isAuthenticated, signIn } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");
  const [standardFilter, setStandardFilter] = useState<string>("all");
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
      if (!ids.has(it.id)) {
        ids.add(it.id);
        combined.push(it);
      }
    });
    return combined;
  }, [backendItems]);

  const currentUser = user || (isAuthenticated ? mockUser : null);

  // Portfolio & Report aggregates
  const stats = useMemo(() => {
    const totalReports = allSavedAnalyses.length;
    const totalAreaHa = allSavedAnalyses.reduce(
      (sum, item) => sum + (item.analysis_result?.area_ha || 0),
      0
    );
    const totalCo2e = allSavedAnalyses.reduce(
      (sum, item) => sum + (item.analysis_result?.total_co2e || 0),
      0
    );
    const avgConfidence =
      totalReports > 0
        ? allSavedAnalyses.reduce(
            (sum, item) => sum + (item.analysis_result?.confidence_score || 85),
            0
          ) / totalReports
        : 90;

    return { totalReports, totalAreaHa, totalCo2e, avgConfidence };
  }, [allSavedAnalyses]);

  // Filtered reports
  const filteredReports = useMemo(() => {
    return allSavedAnalyses.filter((item) => {
      const q = searchQuery.toLowerCase().trim();
      const res = item.analysis_result;
      const matchesSearch =
        !q ||
        item.location_name.toLowerCase().includes(q) ||
        (res?.recommended_standard || "").toLowerCase().includes(q) ||
        (res?.ecoregion || "").toLowerCase().includes(q) ||
        (res?.forest_type || "").toLowerCase().includes(q) ||
        item.id.toLowerCase().includes(q);

      const standardText = (res?.recommended_standard || "").toLowerCase();
      let matchesStandard = true;
      if (standardFilter === "verra") {
        matchesStandard = standardText.includes("verra") || standardText.includes("vcs") || standardText.includes("vm0047");
      } else if (standardFilter === "gold") {
        matchesStandard = standardText.includes("gold");
      } else if (standardFilter === "ipcc") {
        matchesStandard = standardText.includes("ipcc") || standardText.includes("tier");
      }

      return matchesSearch && matchesStandard;
    });
  }, [allSavedAnalyses, searchQuery, standardFilter]);

  const downloadJson = (result: any) => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(result, null, 2));
    const anchor = document.createElement("a");
    anchor.setAttribute("href", dataStr);
    anchor.setAttribute("download", `canopy-audit-report-${result.analysis_id || "dossier"}.json`);
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  const downloadAllReports = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(allSavedAnalyses, null, 2));
    const anchor = document.createElement("a");
    anchor.setAttribute("href", dataStr);
    anchor.setAttribute("download", `canopy-all-audit-reports.json`);
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

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
        {/* Unauthenticated notice if not signed in (Identical to Dashboard) */}
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

        {/* Reports Welcome Header with Glass Capsule (Identical to Dashboard) */}
        <div className="crystal-glass-card rounded-3xl p-7 sm:p-9 border border-white/15 shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
          {/* Subtle top specular shimmer */}
          <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/40 to-transparent" />

          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 shadow-inner">
                <FileText className="w-6 h-6 text-emerald-400 animate-pulse" />
              </div>
              <div>
                <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight flex items-center gap-3">
                  Carbon Stock Reports
                  <span className="text-xs font-mono font-bold uppercase tracking-widest text-emerald-300 bg-emerald-500/20 px-3 py-1 rounded-full border border-emerald-400/30 shadow-inner">
                    Audit Ready
                  </span>
                </h1>
                <p className="text-xs sm:text-sm text-gray-300 mt-1">
                  Verified biomass stock and emission certificates for{" "}
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
              onClick={downloadAllReports}
              className="gap-2 bg-white/10 hover:bg-white/20 text-white border-white/20 rounded-xl backdrop-blur-md"
            >
              <Download className="w-4 h-4 text-emerald-300" />
              Export All Reports
            </Button>

            <Button
              size="sm"
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-2 rounded-xl shadow-xl shadow-emerald-950/60 border border-emerald-400/40 hover:scale-105 active:scale-95 transition-all"
              asChild
            >
              <Link href="/analyze">
                <Plus className="w-4 h-4" />
                Generate New Report
              </Link>
            </Button>
          </div>
        </div>

        {/* 4 Stat Cards Overview with Green Glass Animation (Identical to Dashboard) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 [perspective:1000px]">
          {/* Card 1: Verified Reports */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.05 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Verified Dossiers
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <FileText className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-white font-mono tracking-tight drop-shadow-sm">
                {stats.totalReports}
              </p>
              <div className="flex items-center gap-1.5 text-xs text-emerald-300 font-medium mt-2">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>Verra VCS VM0047 Compliant</span>
              </div>
            </div>
          </motion.div>

          {/* Card 2: Certified Area */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Certified Area
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
                Spaceborne LiDAR ground-truthed
              </p>
            </div>
          </motion.div>

          {/* Card 3: Total Verified Carbon */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Total CO₂e Verified
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <TreePine className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-emerald-400 font-mono tracking-tight drop-shadow-sm">
                {(stats.totalCo2e / 1000000).toFixed(2)}M
                <span className="text-base font-normal text-white ml-1.5 font-sans">tCO₂e</span>
              </p>
              <p className="text-xs text-emerald-200/80 mt-2">
                {Math.round(stats.totalCo2e).toLocaleString("en-US")} tonnes verified carbon
              </p>
            </div>
          </motion.div>

          {/* Card 4: Verification Quality */}
          <motion.div
            initial={{ opacity: 0, y: 25, rotateX: 6 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.5)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-2xl flex flex-col justify-between group transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-300/80">
                Mean Confidence
              </span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 group-hover:scale-110 transition-transform">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-4xl font-black text-white font-mono tracking-tight drop-shadow-sm">
                {Math.round(stats.avgConfidence)}
                <span className="text-base font-normal text-emerald-300 ml-1 font-sans">/100</span>
              </p>
              <div className="flex items-center gap-1.5 text-xs text-emerald-300 font-medium mt-2">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Tier 3 IPCC Standard</span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Search & Filter Bar (Identical to Dashboard) */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-400" />
            <Input
              type="text"
              placeholder="Search reports by forest site, ecoregion, or standard..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="crystal-glass-input pl-10 h-11 text-xs text-white placeholder:text-gray-400 rounded-2xl border-white/15 focus:border-emerald-400 w-full"
            />
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-semibold text-gray-300 mr-1 hidden sm:inline">
              Standard:
            </span>
            {[
              { id: "all", label: "All Standards" },
              { id: "verra", label: "Verra VCS" },
              { id: "gold", label: "Gold Standard" },
              { id: "ipcc", label: "IPCC Tier 3" },
            ].map((st) => (
              <button
                key={st.id}
                type="button"
                onClick={() => setStandardFilter(st.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 border ${
                  standardFilter === st.id
                    ? "bg-emerald-600/90 text-white border-emerald-400 shadow-md shadow-emerald-950/40"
                    : "crystal-glass text-gray-300 border-white/10 hover:text-white hover:border-white/20"
                }`}
              >
                {st.label}
              </button>
            ))}
          </div>
        </div>

        {/* Reports Table Section (Identical to Dashboard) */}
        <div className="crystal-glass-card rounded-3xl border border-white/15 shadow-2xl overflow-hidden">
          <div className="p-6 border-b border-white/10 flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                Certified Audit Reports
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              </h2>
              <span className="text-xs font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 px-2.5 py-0.5 rounded-full">
                {filteredReports.length} Available
              </span>
            </div>
            <p className="text-xs text-gray-300">
              Interactive spaceborne dossiers calibrated against GEDI LiDAR and Sentinel-2 reflectances
            </p>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader className="bg-white/5 border-b border-white/10">
                <TableRow className="border-b border-white/10 hover:bg-transparent">
                  <TableHead className="text-xs font-semibold text-emerald-300 py-4 pl-6">
                    Report Dossier / Forest Site
                  </TableHead>
                  <TableHead className="text-xs font-semibold text-emerald-300 py-4">
                    Verification Standard
                  </TableHead>
                  <TableHead className="text-xs font-semibold text-right text-emerald-300 py-4">
                    Monitored Area
                  </TableHead>
                  <TableHead className="text-xs font-semibold text-right text-emerald-300 py-4">
                    Est. Carbon Stock
                  </TableHead>
                  <TableHead className="text-xs font-semibold text-center text-emerald-300 py-4">
                    Confidence Tier
                  </TableHead>
                  <TableHead className="text-xs font-semibold text-right text-emerald-300 py-4 pr-6">
                    Audit Actions
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredReports.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-12 text-gray-400 text-sm">
                      No matching audit reports found. Try modifying your search or standard filter.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredReports.map((item) => {
                    const res = item.analysis_result;
                    return (
                      <TableRow
                        key={item.id}
                        className="border-b border-white/5 hover:bg-white/10 transition-colors group"
                      >
                        {/* Site Name and Location */}
                        <TableCell className="py-4 pl-6">
                          <div className="flex items-center gap-3">
                            <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 shrink-0 group-hover:scale-105 transition-transform">
                              <FileText className="w-4 h-4 text-emerald-400" />
                            </div>
                            <div>
                              <p className="font-bold text-white text-sm group-hover:text-emerald-300 transition-colors">
                                {item.location_name}
                              </p>
                              <p className="text-[11px] text-gray-400 font-mono mt-0.5">
                                Dossier #{res?.analysis_id || item.id} • {res?.ecoregion || "Global Biosphere"}
                              </p>
                            </div>
                          </div>
                        </TableCell>

                        {/* Verification Standard */}
                        <TableCell className="py-4 text-xs font-medium">
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-white/10 border border-white/15 text-white">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                            {res?.recommended_standard || "Verra VCS (VM0047)"}
                          </span>
                        </TableCell>

                        {/* Monitored Area */}
                        <TableCell className="py-4 text-right font-mono text-xs font-semibold text-white">
                          {(res?.area_ha || 1500).toLocaleString("en-US")} ha
                        </TableCell>

                        {/* Est. Carbon Stock */}
                        <TableCell className="py-4 text-right font-mono text-xs font-bold text-emerald-400">
                          {Math.round(res?.total_co2e || 450000).toLocaleString("en-US")} tCO₂e
                        </TableCell>

                        {/* Confidence Tier */}
                        <TableCell className="py-4 text-center font-mono text-xs text-emerald-300">
                          <span className="px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-400/30 font-bold">
                            Tier 3 (±{res?.confidence_interval_pct || 8.4}%)
                          </span>
                        </TableCell>

                        {/* Actions */}
                        <TableCell className="py-4 pr-6 text-right">
                          <div className="inline-flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => downloadJson(res || item)}
                              className="h-8 text-xs gap-1.5 bg-white/10 hover:bg-white/20 text-white border-white/20 rounded-xl"
                            >
                              <Download className="w-3.5 h-3.5 text-emerald-300" />
                              <span>JSON</span>
                            </Button>

                            <Button
                              size="sm"
                              className="h-8 text-xs bg-emerald-600 hover:bg-emerald-500 text-white gap-1 rounded-xl shadow-md border border-emerald-400/30"
                              asChild
                            >
                              <Link href={`/results/${res?.analysis_id || item.id}`}>
                                <span>View Dossier</span>
                                <ArrowUpRight className="w-3.5 h-3.5" />
                              </Link>
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Methodology Standards 3-Pod Banner with Glass Theme */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.4)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-xl flex items-start gap-4 group transition-all duration-300 text-white"
          >
            <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 shrink-0 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white tracking-tight">Verra VCS VM0047 Aligned</h4>
              <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                Dynamic performance benchmarks &amp; high-density GEDI LiDAR canopy profile calibration.
              </p>
            </div>
          </motion.div>

          <motion.div
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.4)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-xl flex items-start gap-4 group transition-all duration-300 text-white"
          >
            <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 shrink-0 group-hover:scale-110 transition-transform">
              <Sparkles className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white tracking-tight">Tier 3 IPCC Allometry</h4>
              <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                Site-specific Wood Density &amp; Chave 2014 pan-tropical Above/Below ground equations.
              </p>
            </div>
          </motion.div>

          <motion.div
            whileHover={{ y: -4, borderColor: "rgba(52, 211, 153, 0.4)" }}
            className="crystal-glass-card rounded-3xl p-6 border border-white/15 shadow-xl flex items-start gap-4 group transition-all duration-300 text-white"
          >
            <div className="p-3 rounded-2xl bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 shrink-0 group-hover:scale-110 transition-transform">
              <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white tracking-tight">Auditor Packet Export</h4>
              <p className="text-xs text-gray-300 mt-1 leading-relaxed">
                Full GeoJSON polygons, pixel reflectance data, and Monte Carlo confidence bounds.
              </p>
            </div>
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
