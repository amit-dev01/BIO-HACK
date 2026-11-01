"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { useAuth } from "@/context/AuthContext";
import { mockSavedAnalyses, mockUser } from "@/lib/mock-data";
import { SavedAnalysis } from "@/lib/types";
import {
  TreePine,
  Plus,
  Search,
  Filter,
  Download,
  ExternalLink,
  ShieldCheck,
  TrendingUp,
  MapPin,
  Calendar,
  Layers,
  ArrowUpRight,
  Sparkles,
  BarChart3,
  CheckCircle2,
  Clock,
  AlertTriangle,
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
  React.useEffect(() => {
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
      .catch((err) => console.warn("Backend listAnalyses error:", err));

    return () => {
      isMounted = false;
    };
  }, []);

  const allSavedAnalyses = useMemo(() => {
    // Combine backend items with mock items avoiding duplicate IDs
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
    <div className="flex flex-col min-h-screen bg-[#F5F5F0] text-gray-900">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 space-y-8">
        {/* Unauthenticated notice if not signed in */}
        {!isAuthenticated && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xs">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-amber-100 text-amber-800">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-amber-900 text-sm">You are viewing demo research plots</h4>
                <p className="text-xs text-amber-700">
                  Sign in or use our one-click demo session to unlock full live telemetry and report export.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                size="sm"
                variant="outline"
                onClick={() => signIn("elena.rostova@canopyai.earth", "password")}
                className="bg-white border-amber-300 text-amber-900 hover:bg-amber-100"
              >
                Sign In as Dr. Elena
              </Button>
              <Button size="sm" className="bg-forest hover:bg-green-700 text-white" asChild>
                <Link href="/login">Log In</Link>
              </Button>
            </div>
          </div>
        )}

        {/* Dashboard Welcome Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-200">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
                Project Dashboard
              </h1>
              <Badge className="bg-green-100 text-green-800 hover:bg-green-100 border-green-200 font-mono text-xs">
                Developer Pro Plan
              </Badge>
            </div>
            <p className="text-sm text-gray-500">
              Welcome back,{" "}
              <span className="font-semibold text-gray-800">
                {currentUser?.full_name || "Dr. Elena Rostova"}
              </span>
              . Here is an overview of your monitored carbon tracts.
            </p>
          </div>

          <div className="flex items-center gap-3">
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
              className="gap-2 bg-white"
            >
              <Download className="w-4 h-4 text-gray-500" />
              Export Portfolio
            </Button>

            <Button
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white gap-2 shadow-xs"
              asChild
            >
              <Link href="/analyze">
                <Plus className="w-4 h-4" />
                New Forest Analysis
              </Link>
            </Button>
          </div>
        </div>

        {/* Stat Cards Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Total Analyses */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Completed Analyses
              </span>
              <div className="p-2 rounded-xl bg-green-50 text-green-700">
                <Layers className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-gray-900 font-mono">
                {stats.totalAnalyses}
              </p>
              <p className="text-xs text-green-700 font-medium flex items-center gap-1 mt-1">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>All plots verified (Tier 3)</span>
              </p>
            </div>
          </div>

          {/* Card 2: Total Area Monitored */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Area Monitored
              </span>
              <div className="p-2 rounded-xl bg-green-50 text-green-700">
                <MapPin className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-gray-900 font-mono">
                {Math.round(stats.totalAreaHa).toLocaleString()}
                <span className="text-sm font-normal text-gray-500 ml-1">ha</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Across Amazon, Congo, and Borneo basins
              </p>
            </div>
          </div>

          {/* Card 3: Total Carbon Stock */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Total CO₂e Stored
              </span>
              <div className="p-2 rounded-xl bg-green-50 text-green-700">
                <TreePine className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-gray-900 font-mono">
                {(stats.totalCo2e / 1000000).toFixed(2)}M
                <span className="text-sm font-normal text-gray-500 ml-1">tCO₂e</span>
              </p>
              <p className="text-xs text-green-700 font-medium flex items-center gap-1 mt-1">
                <Sparkles className="w-3.5 h-3.5" />
                <span>+303k tCO₂e / yr sequestration</span>
              </p>
            </div>
          </div>

          {/* Card 4: Estimated Crediting Value */}
          <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                Annual Est. Revenue
              </span>
              <div className="p-2 rounded-xl bg-green-50 text-green-700">
                <BarChart3 className="w-5 h-5" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold text-gray-900 font-mono">
                $4.55M
                <span className="text-sm font-normal text-gray-500 ml-1">USD</span>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Based on $15.00 / tCO₂e benchmark
              </p>
            </div>
          </div>
        </div>

        {/* Saved Analyses Section */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-xs overflow-hidden">
          {/* Table Toolbar */}
          <div className="p-6 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                Monitored Forest Sites
              </h2>
              <p className="text-xs text-gray-500">
                Real-time satellite MRV plots with ongoing optical &amp; radar telemetry
              </p>
            </div>

            <div className="flex items-center gap-3">
              {/* Search Bar */}
              <div className="relative">
                <Input
                  placeholder="Filter by plot name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 h-9 text-xs w-48 sm:w-64 bg-gray-50 border-gray-200"
                />
                <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-3 pointer-events-none" />
              </div>

              {/* Status Select */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="h-9 px-3 rounded-md border border-gray-200 bg-gray-50 text-xs font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-600"
              >
                <option value="all">All Statuses</option>
                <option value="complete">Complete</option>
                <option value="processing">Processing</option>
              </select>
            </div>
          </div>

          {/* Table */}
          {filteredAnalyses.length === 0 ? (
            <div className="text-center py-16 px-4">
              <TreePine className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <h3 className="text-base font-bold text-gray-800">No matching forest plots found</h3>
              <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 mb-6">
                Try adjusting your search query or draw a new boundary in the satellite analyzer.
              </p>
              <Button size="sm" className="bg-forest text-white" asChild>
                <Link href="/analyze">Start New Analysis</Link>
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-gray-50/70">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Forest Tract / Location</TableHead>
                    <TableHead className="text-xs font-semibold">Ecoregion</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Area (ha)</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Total Biomass</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Total CO₂e</TableHead>
                    <TableHead className="text-xs font-semibold text-center">Confidence</TableHead>
                    <TableHead className="text-xs font-semibold text-center">Status</TableHead>
                    <TableHead className="text-xs font-semibold text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAnalyses.map((item) => {
                    const res = item.analysis_result;
                    const dateFormatted = new Date(item.created_at).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    });

                    return (
                      <TableRow key={item.id} className="hover:bg-gray-50/80 transition-colors">
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-green-50 text-forest shrink-0">
                              <TreePine className="w-4 h-4" />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900 text-sm">
                                {item.location_name}
                              </p>
                              <p className="text-[11px] text-gray-400 font-mono">
                                ID: {res.analysis_id} • {dateFormatted}
                              </p>
                            </div>
                          </div>
                        </TableCell>

                        <TableCell className="text-xs text-gray-600 max-w-[200px] truncate">
                          {res.ecoregion}
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs font-semibold text-gray-800">
                          {res.area_ha.toLocaleString()}
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs text-gray-700">
                          {res.total_biomass_t_per_ha.toFixed(1)} t/ha
                        </TableCell>

                        <TableCell className="text-right font-mono text-xs font-bold text-green-700">
                          {Math.round(res.total_co2e).toLocaleString()} t
                        </TableCell>

                        <TableCell className="text-center">
                          <span className="inline-flex items-center gap-1 font-mono text-[11px] font-semibold bg-green-50 text-green-800 px-2 py-0.5 rounded-full border border-green-200">
                            <ShieldCheck className="w-3 h-3 text-green-600" />
                            {Math.round(res.confidence_score)}%
                          </span>
                        </TableCell>

                        <TableCell className="text-center">
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-green-700 bg-green-100/60 px-2.5 py-0.5 rounded-full">
                            <CheckCircle2 className="w-3 h-3 text-green-600" />
                            Complete
                          </span>
                        </TableCell>

                        <TableCell className="text-right">
                          <div className="inline-flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 text-xs text-green-700 hover:text-green-800 hover:bg-green-50 gap-1"
                              asChild
                            >
                              <Link href={`/results/${res.analysis_id}`}>
                                <span>View Report</span>
                                <ArrowUpRight className="w-3.5 h-3.5" />
                              </Link>
                            </Button>
                          </div>
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
