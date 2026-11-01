"use client";

import React, { useState } from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import { mockSavedAnalyses } from "@/lib/mock-data";
import {
  FileText,
  Download,
  ExternalLink,
  ShieldCheck,
  Search,
  Filter,
  CheckCircle2,
  TreePine,
  Sparkles,
  ArrowUpRight,
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

export default function ReportsPage() {
  const [search, setSearch] = useState("");

  const filtered = mockSavedAnalyses.filter(
    (item) =>
      item.location_name.toLowerCase().includes(search.toLowerCase()) ||
      item.analysis_result.recommended_standard.toLowerCase().includes(search.toLowerCase())
  );

  const downloadJson = (result: any) => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(result, null, 2));
    const anchor = document.createElement("a");
    anchor.setAttribute("href", dataStr);
    anchor.setAttribute("download", `audit-report-${result.analysis_id}.json`);
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F5F0] text-gray-900">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-200">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
                Carbon Stock Reports
              </h1>
              <Badge className="bg-green-100 text-green-800 border-green-200 font-mono text-xs">
                Audit Ready
              </Badge>
            </div>
            <p className="text-sm text-gray-500">
              Verified biomass stock and emission reduction certificates formatted for Verra VCS &amp; Gold Standard.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              className="bg-green-600 hover:bg-green-700 text-white gap-2 shadow-xs"
              asChild
            >
              <Link href="/analyze">
                <TreePine className="w-4 h-4" />
                Generate New Report
              </Link>
            </Button>
          </div>
        </div>

        {/* Methodology Standards Banner */}
        <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-xs grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-green-50 text-green-700 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">Verra VCS VM0047</h4>
              <p className="text-xs text-gray-500 mt-0.5">
                Dynamic performance benchmarks &amp; high-density LiDAR canopy height verification.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-green-50 text-green-700 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">Tier 3 IPCC Allometry</h4>
              <p className="text-xs text-gray-500 mt-0.5">
                Site-specific Wood Density &amp; Chave 2014 pan-tropical biomass equations.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-green-50 text-green-700 shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-gray-900">Auditor Export</h4>
              <p className="text-xs text-gray-500 mt-0.5">
                Full GeoJSON polygons, pixel-level reflectance data, and Monte Carlo confidence bounds.
              </p>
            </div>
          </div>
        </div>

        {/* Reports Table Section */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-xs overflow-hidden">
          <div className="p-6 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Available Reports</h2>
              <p className="text-xs text-gray-500">
                Click any report to view comprehensive telemetry or download the raw JSON audit packet.
              </p>
            </div>

            <div className="relative">
              <Input
                placeholder="Search reports by site..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 h-9 text-xs w-48 sm:w-64 bg-gray-50 border-gray-200"
              />
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-3 pointer-events-none" />
            </div>
          </div>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader className="bg-gray-50/70">
                <TableRow>
                  <TableHead className="text-xs font-semibold">Report Title / Site</TableHead>
                  <TableHead className="text-xs font-semibold">Verification Standard</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Monitored Area</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Est. Carbon Stock</TableHead>
                  <TableHead className="text-xs font-semibold text-center">Uncertainty</TableHead>
                  <TableHead className="text-xs font-semibold text-right">Export Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((item) => {
                  const res = item.analysis_result;
                  return (
                    <TableRow key={item.id} className="hover:bg-gray-50/80 transition-colors">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-xl bg-green-50 text-forest shrink-0">
                            <FileText className="w-4 h-4" />
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900 text-sm">
                              {item.location_name}
                            </p>
                            <p className="text-[11px] text-gray-400 font-mono">
                              Report #{res.analysis_id}
                            </p>
                          </div>
                        </div>
                      </TableCell>

                      <TableCell className="text-xs text-gray-700 font-medium">
                        {res.recommended_standard}
                      </TableCell>

                      <TableCell className="text-right font-mono text-xs font-semibold text-gray-800">
                        {res.area_ha.toLocaleString()} ha
                      </TableCell>

                      <TableCell className="text-right font-mono text-xs font-bold text-green-700">
                        {Math.round(res.total_co2e).toLocaleString()} tCO₂e
                      </TableCell>

                      <TableCell className="text-center font-mono text-xs text-gray-600">
                        ±{res.confidence_interval_pct}%
                      </TableCell>

                      <TableCell className="text-right">
                        <div className="inline-flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadJson(res)}
                            className="h-8 text-xs gap-1"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>JSON</span>
                          </Button>

                          <Button
                            size="sm"
                            className="h-8 text-xs bg-forest text-white gap-1"
                            asChild
                          >
                            <Link href={`/results/${res.analysis_id}`}>
                              <span>Full Report</span>
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
        </div>
      </main>

      <Footer />
    </div>
  );
}
